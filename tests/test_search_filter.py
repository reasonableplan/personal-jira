import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.enums import IssuePriority, IssueStatus, IssueType
from src.personal_jira.models.issue import Issue

API_BASE = "/api/v1/issues"


async def _seed_issues(db: AsyncSession) -> list[Issue]:
    issues_data = [
        {
            "title": "Auth login bug",
            "issue_type": IssueType.BUG,
            "status": IssueStatus.TODO,
            "priority": IssuePriority.CRITICAL,
            "assignee": "alice",
        },
        {
            "title": "Dashboard redesign",
            "issue_type": IssueType.STORY,
            "status": IssueStatus.IN_PROGRESS,
            "priority": IssuePriority.HIGH,
            "assignee": "bob",
        },
        {
            "title": "Refactor auth module",
            "issue_type": IssueType.TASK,
            "status": IssueStatus.BACKLOG,
            "priority": IssuePriority.MEDIUM,
            "assignee": "alice",
        },
        {
            "title": "Epic: Q2 goals",
            "issue_type": IssueType.EPIC,
            "status": IssueStatus.TODO,
            "priority": IssuePriority.HIGH,
            "assignee": None,
        },
        {
            "title": "Fix pagination bug",
            "issue_type": IssueType.BUG,
            "status": IssueStatus.DONE,
            "priority": IssuePriority.LOW,
            "assignee": "charlie",
        },
    ]
    created: list[Issue] = []
    for d in issues_data:
        issue = Issue(id=uuid.uuid4(), **d)
        db.add(issue)
        created.append(issue)
    await db.commit()
    for issue in created:
        await db.refresh(issue)
    return created


class TestFilterByStatus:
    async def test_filter_single_status(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"status": IssueStatus.TODO.value})
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["status"] == IssueStatus.TODO.value

    async def test_filter_done_status(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"status": IssueStatus.DONE.value})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Fix pagination bug"


class TestFilterByPriority:
    async def test_filter_critical_priority(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE, params={"priority": IssuePriority.CRITICAL.value}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["priority"] == IssuePriority.CRITICAL.value

    async def test_filter_high_priority(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE, params={"priority": IssuePriority.HIGH.value}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2


class TestFilterByIssueType:
    async def test_filter_bug_type(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE, params={"issue_type": IssueType.BUG.value}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["issue_type"] == IssueType.BUG.value

    async def test_filter_epic_type(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE, params={"issue_type": IssueType.EPIC.value}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1


class TestFilterByAssignee:
    async def test_filter_by_assignee(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"assignee": "alice"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["assignee"] == "alice"

    async def test_filter_nonexistent_assignee(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"assignee": "nobody"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 0


class TestSearchByTitle:
    async def test_search_keyword(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"search": "auth"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 2
        for item in data["items"]:
            assert "auth" in item["title"].lower()

    async def test_search_no_match(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"search": "zzzznonexistent"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 0

    async def test_search_case_insensitive(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"search": "AUTH"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 2


class TestCombinedFilters:
    async def test_status_and_priority(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE,
            params={
                "status": IssueStatus.TODO.value,
                "priority": IssuePriority.HIGH.value,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["status"] == IssueStatus.TODO.value
            assert item["priority"] == IssuePriority.HIGH.value

    async def test_type_and_assignee(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE,
            params={
                "issue_type": IssueType.BUG.value,
                "assignee": "alice",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Auth login bug"

    async def test_search_with_status_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE,
            params={"search": "bug", "status": IssueStatus.DONE.value},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Fix pagination bug"

    async def test_all_filters_combined(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE,
            params={
                "status": IssueStatus.TODO.value,
                "priority": IssuePriority.CRITICAL.value,
                "issue_type": IssueType.BUG.value,
                "assignee": "alice",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Auth login bug"


class TestPaginationWithFilters:
    async def test_pagination_offset_limit(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"offset": 0, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    async def test_pagination_second_page(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(API_BASE, params={"offset": 2, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

    async def test_pagination_with_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        await _seed_issues(db_session)
        resp = await client.get(
            API_BASE,
            params={
                "issue_type": IssueType.BUG.value,
                "offset": 0,
                "limit": 1,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["total"] == 2

    async def test_empty_result_set(
        self, client: AsyncClient, db_session: AsyncSession
    ) -> None:
        resp = await client.get(API_BASE, params={"offset": 0, "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
