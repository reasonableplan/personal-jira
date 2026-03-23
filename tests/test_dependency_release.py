import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.dependency import IssueDependency
from src.personal_jira.models.enums import IssuePriority, IssueStatus, IssueType
from src.personal_jira.models.issue import Issue
from src.personal_jira.services.dependency_release_service import (
    DependencyReleaseService,
)
from src.personal_jira.services.dependency_service import DependencyService

API_BASE = "/api/v1/issues"
DEP_BASE = "/api/v1/issues/{issue_id}/dependencies"


async def _create_issue(
    db: AsyncSession,
    title: str,
    status: IssueStatus = IssueStatus.BACKLOG,
    issue_type: IssueType = IssueType.TASK,
) -> Issue:
    issue = Issue(
        id=uuid.uuid4(),
        title=title,
        issue_type=issue_type,
        status=status,
        priority=IssuePriority.MEDIUM,
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


async def _create_dependency(
    db: AsyncSession, issue_id: uuid.UUID, depends_on_id: uuid.UUID
) -> IssueDependency:
    dep = IssueDependency(issue_id=issue_id, depends_on_id=depends_on_id)
    db.add(dep)
    await db.commit()
    return dep


class TestDependencyAutoRelease:
    async def test_single_blocker_done_releases_blocked(
        self, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(db_session, "Blocker", IssueStatus.TODO)
        blocked = await _create_issue(db_session, "Blocked", IssueStatus.BACKLOG)
        await _create_dependency(db_session, blocked.id, blocker.id)

        blocker.status = IssueStatus.DONE
        await db_session.commit()

        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(blocker.id)

        await db_session.refresh(blocked)
        assert blocked.status == IssueStatus.TODO

    async def test_partial_blockers_done_keeps_blocked(
        self, db_session: AsyncSession
    ) -> None:
        blocker1 = await _create_issue(db_session, "Blocker 1", IssueStatus.DONE)
        blocker2 = await _create_issue(db_session, "Blocker 2", IssueStatus.TODO)
        blocked = await _create_issue(db_session, "Blocked", IssueStatus.BACKLOG)
        await _create_dependency(db_session, blocked.id, blocker1.id)
        await _create_dependency(db_session, blocked.id, blocker2.id)

        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(blocker1.id)

        await db_session.refresh(blocked)
        assert blocked.status == IssueStatus.BACKLOG

    async def test_all_blockers_done_releases_blocked(
        self, db_session: AsyncSession
    ) -> None:
        blocker1 = await _create_issue(db_session, "Blocker 1", IssueStatus.DONE)
        blocker2 = await _create_issue(db_session, "Blocker 2", IssueStatus.TODO)
        blocked = await _create_issue(db_session, "Blocked", IssueStatus.BACKLOG)
        await _create_dependency(db_session, blocked.id, blocker1.id)
        await _create_dependency(db_session, blocked.id, blocker2.id)

        blocker2.status = IssueStatus.DONE
        await db_session.commit()

        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(blocker2.id)

        await db_session.refresh(blocked)
        assert blocked.status == IssueStatus.TODO

    async def test_no_dependencies_noop(
        self, db_session: AsyncSession
    ) -> None:
        issue = await _create_issue(db_session, "Standalone", IssueStatus.DONE)
        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(issue.id)

    async def test_non_backlog_issue_not_transitioned(
        self, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(db_session, "Blocker", IssueStatus.TODO)
        blocked = await _create_issue(db_session, "Blocked", IssueStatus.IN_PROGRESS)
        await _create_dependency(db_session, blocked.id, blocker.id)

        blocker.status = IssueStatus.DONE
        await db_session.commit()

        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(blocker.id)

        await db_session.refresh(blocked)
        assert blocked.status == IssueStatus.IN_PROGRESS

    async def test_multiple_blocked_issues_released(
        self, db_session: AsyncSession
    ) -> None:
        blocker = await _create_issue(db_session, "Blocker", IssueStatus.TODO)
        blocked1 = await _create_issue(db_session, "Blocked 1", IssueStatus.BACKLOG)
        blocked2 = await _create_issue(db_session, "Blocked 2", IssueStatus.BACKLOG)
        await _create_dependency(db_session, blocked1.id, blocker.id)
        await _create_dependency(db_session, blocked2.id, blocker.id)

        blocker.status = IssueStatus.DONE
        await db_session.commit()

        service = DependencyReleaseService(db_session)
        await service.handle_issue_done(blocker.id)

        await db_session.refresh(blocked1)
        await db_session.refresh(blocked2)
        assert blocked1.status == IssueStatus.TODO
        assert blocked2.status == IssueStatus.TODO


class TestDependencyServiceCycleDetection:
    async def test_self_dependency_rejected(
        self, db_session: AsyncSession
    ) -> None:
        issue = await _create_issue(db_session, "Self Dep")
        service = DependencyService(db_session)
        with pytest.raises(Exception):
            await service.add_dependency(issue.id, issue.id)

    async def test_circular_dependency_rejected(
        self, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")
        c = await _create_issue(db_session, "C")

        service = DependencyService(db_session)
        await service.add_dependency(b.id, a.id)
        await service.add_dependency(c.id, b.id)

        with pytest.raises(Exception):
            await service.add_dependency(a.id, c.id)

    async def test_valid_dependency_chain(
        self, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")
        c = await _create_issue(db_session, "C")

        service = DependencyService(db_session)
        await service.add_dependency(b.id, a.id)
        await service.add_dependency(c.id, b.id)

        result = await db_session.execute(
            select(IssueDependency).where(IssueDependency.issue_id == c.id)
        )
        deps = result.scalars().all()
        assert len(deps) == 1
        assert deps[0].depends_on_id == b.id

    async def test_duplicate_dependency_rejected(
        self, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")

        service = DependencyService(db_session)
        await service.add_dependency(b.id, a.id)

        with pytest.raises(Exception):
            await service.add_dependency(b.id, a.id)


class TestDependencyAPI:
    async def test_add_dependency_via_api(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")

        resp = await client.post(
            f"{API_BASE}/{b.id}/dependencies",
            json={"depends_on_id": str(a.id)},
        )
        assert resp.status_code == 201

    async def test_list_dependencies_via_api(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")
        await _create_dependency(db_session, b.id, a.id)

        resp = await client.get(f"{API_BASE}/{b.id}/dependencies")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    async def test_delete_dependency_via_api(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")
        await _create_dependency(db_session, b.id, a.id)

        resp = await client.delete(
            f"{API_BASE}/{b.id}/dependencies/{a.id}"
        )
        assert resp.status_code in (200, 204)

    async def test_add_circular_dependency_via_api_returns_error(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")
        b = await _create_issue(db_session, "B")
        await _create_dependency(db_session, b.id, a.id)

        resp = await client.post(
            f"{API_BASE}/{a.id}/dependencies",
            json={"depends_on_id": str(b.id)},
        )
        assert resp.status_code in (400, 409, 422)

    async def test_add_self_dependency_via_api_returns_error(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        a = await _create_issue(db_session, "A")

        resp = await client.post(
            f"{API_BASE}/{a.id}/dependencies",
            json={"depends_on_id": str(a.id)},
        )
        assert resp.status_code in (400, 409, 422)
