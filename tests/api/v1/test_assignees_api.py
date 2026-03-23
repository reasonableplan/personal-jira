import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus, IssueType, IssuePriority

API_PREFIX = "/api/v1"


@pytest.fixture
async def sample_issue(db_session: AsyncSession) -> Issue:
    issue = Issue(
        title="Assignee test issue",
        issue_type=IssueType.TASK,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
    )
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


class TestAssignUser:
    async def test_assign_user_to_issue(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
            json={"user_id": "user-1"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"] == "user-1"
        assert "id" in data

    async def test_assign_duplicate_user_returns_409(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
            json={"user_id": "user-1"},
        )
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
            json={"user_id": "user-1"},
        )
        assert resp.status_code == 409

    async def test_assign_to_nonexistent_issue_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"{API_PREFIX}/issues/{fake_id}/assignees",
            json={"user_id": "user-1"},
        )
        assert resp.status_code == 404

    async def test_assign_empty_user_id_returns_422(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
            json={"user_id": ""},
        )
        assert resp.status_code == 422


class TestListAssignees:
    async def test_list_assignees_empty(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/assignees")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_assignees_returns_all(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        for uid in ["user-1", "user-2", "user-3"]:
            await client.post(
                f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
                json={"user_id": uid},
            )
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/assignees")
        assert resp.status_code == 200
        user_ids = {a["user_id"] for a in resp.json()}
        assert user_ids == {"user-1", "user-2", "user-3"}

    async def test_list_assignees_nonexistent_issue_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.get(f"{API_PREFIX}/issues/{fake_id}/assignees")
        assert resp.status_code == 404


class TestRemoveAssignee:
    async def test_remove_assignee(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        create_resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
            json={"user_id": "user-1"},
        )
        assignee_id = create_resp.json()["id"]
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees/{assignee_id}"
        )
        assert resp.status_code == 204

        list_resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/assignees")
        assert list_resp.json() == []

    async def test_remove_nonexistent_assignee_returns_404(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees/{fake_id}"
        )
        assert resp.status_code == 404

    async def test_remove_assignee_multiple_keeps_others(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        ids: list[str] = []
        for uid in ["user-1", "user-2"]:
            r = await client.post(
                f"{API_PREFIX}/issues/{sample_issue.id}/assignees",
                json={"user_id": uid},
            )
            ids.append(r.json()["id"])

        await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/assignees/{ids[0]}"
        )

        list_resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/assignees")
        remaining = list_resp.json()
        assert len(remaining) == 1
        assert remaining[0]["user_id"] == "user-2"
