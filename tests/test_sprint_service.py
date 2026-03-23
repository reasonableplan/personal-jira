import pytest
from datetime import date
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.sprint import Sprint, SprintStatus
from personal_jira.models.issue import Issue
from personal_jira.services.sprint_service import SprintService
from personal_jira.schemas.sprint import SprintCreate, SprintUpdate


class TestSprintServiceCreate:
    @pytest.mark.asyncio
    async def test_create_sprint(self, db_session: AsyncSession):
        data = SprintCreate(
            name="Sprint 1",
            goal="MVP",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        service = SprintService(db_session)
        sprint = await service.create(data)

        assert sprint.id is not None
        assert sprint.name == "Sprint 1"
        assert sprint.goal == "MVP"
        assert sprint.status == SprintStatus.PLANNING


class TestSprintServiceGet:
    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        service = SprintService(db_session)
        result = await service.get_by_id(sprint.id)
        assert result is not None
        assert result.id == sprint.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        service = SprintService(db_session)
        result = await service.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_list_sprints(self, db_session: AsyncSession):
        for i in range(3):
            db_session.add(Sprint(
                name=f"Sprint {i}",
                start_date=date(2026, 3, 23),
                end_date=date(2026, 4, 6),
            ))
        await db_session.commit()

        service = SprintService(db_session)
        sprints, total = await service.list_sprints(offset=0, limit=10)
        assert total == 3
        assert len(sprints) == 3

    @pytest.mark.asyncio
    async def test_list_sprints_pagination(self, db_session: AsyncSession):
        for i in range(5):
            db_session.add(Sprint(
                name=f"Sprint {i}",
                start_date=date(2026, 3, 23),
                end_date=date(2026, 4, 6),
            ))
        await db_session.commit()

        service = SprintService(db_session)
        sprints, total = await service.list_sprints(offset=0, limit=2)
        assert total == 5
        assert len(sprints) == 2

    @pytest.mark.asyncio
    async def test_list_sprints_filter_status(self, db_session: AsyncSession):
        db_session.add(Sprint(
            name="Active",
            status=SprintStatus.ACTIVE,
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        ))
        db_session.add(Sprint(
            name="Planning",
            start_date=date(2026, 4, 6),
            end_date=date(2026, 4, 20),
        ))
        await db_session.commit()

        service = SprintService(db_session)
        sprints, total = await service.list_sprints(
            offset=0, limit=10, status=SprintStatus.ACTIVE
        )
        assert total == 1
        assert sprints[0].name == "Active"


class TestSprintServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_sprint(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        service = SprintService(db_session)
        updated = await service.update(
            sprint.id, SprintUpdate(name="Updated", status="active")
        )
        assert updated is not None
        assert updated.name == "Updated"
        assert updated.status == SprintStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session: AsyncSession):
        service = SprintService(db_session)
        result = await service.update(uuid4(), SprintUpdate(name="X"))
        assert result is None


class TestSprintServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_sprint(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        service = SprintService(db_session)
        deleted = await service.delete(sprint.id)
        assert deleted is True

        result = await service.get_by_id(sprint.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session: AsyncSession):
        service = SprintService(db_session)
        deleted = await service.delete(uuid4())
        assert deleted is False


class TestSprintServiceIssues:
    @pytest.mark.asyncio
    async def test_add_issue_to_sprint(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        issue = Issue(title="Task 1")
        db_session.add_all([sprint, issue])
        await db_session.commit()
        await db_session.refresh(sprint)
        await db_session.refresh(issue)

        service = SprintService(db_session)
        result = await service.add_issue(sprint.id, issue.id)
        assert result is True

        await db_session.refresh(issue)
        assert issue.sprint_id == sprint.id

    @pytest.mark.asyncio
    async def test_add_issue_sprint_not_found(self, db_session: AsyncSession):
        issue = Issue(title="Task 1")
        db_session.add(issue)
        await db_session.commit()
        await db_session.refresh(issue)

        service = SprintService(db_session)
        result = await service.add_issue(uuid4(), issue.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_add_issue_not_found(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        service = SprintService(db_session)
        result = await service.add_issue(sprint.id, uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_issue_from_sprint(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        issue = Issue(title="Task 1")
        db_session.add_all([sprint, issue])
        await db_session.commit()
        await db_session.refresh(sprint)
        await db_session.refresh(issue)

        issue.sprint_id = sprint.id
        await db_session.commit()

        service = SprintService(db_session)
        result = await service.remove_issue(sprint.id, issue.id)
        assert result is True

        await db_session.refresh(issue)
        assert issue.sprint_id is None

    @pytest.mark.asyncio
    async def test_get_sprint_issues(self, db_session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        for i in range(3):
            db_session.add(Issue(title=f"Task {i}", sprint_id=sprint.id))
        await db_session.commit()

        service = SprintService(db_session)
        issues = await service.get_sprint_issues(sprint.id)
        assert len(issues) == 3
