import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus, IssueType, IssuePriority

API_PREFIX = "/api/v1"


@pytest.fixture
async def sample_issue(db_session: AsyncSession) -> Issue:
    issue = Issue(
        title="Label test issue",
        issue_type=IssueType.TASK,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
    )
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


class TestAddLabel:
    async def test_add_label_to_issue(self, client: AsyncClient, sample_issue: Issue) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels",
            json={"name": "backend"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "backend"
        assert "id" in data

    async def test_add_duplicate_label_returns_409(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels",
            json={"name": "backend"},
        )
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels",
            json={"name": "backend"},
        )
        assert resp.status_code == 409

    async def test_add_label_to_nonexistent_issue_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"{API_PREFIX}/issues/{fake_id}/labels",
            json={"name": "backend"},
        )
        assert resp.status_code == 404

    async def test_add_label_empty_name_returns_422(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels",
            json={"name": ""},
        )
        assert resp.status_code == 422


class TestListLabels:
    async def test_list_labels_empty(self, client: AsyncClient, sample_issue: Issue) -> None:
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/labels")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_labels_returns_all(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        for name in ["backend", "urgent", "v2"]:
            await client.post(
                f"{API_PREFIX}/issues/{sample_issue.id}/labels",
                json={"name": name},
            )
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/labels")
        assert resp.status_code == 200
        names = {label["name"] for label in resp.json()}
        assert names == {"backend", "urgent", "v2"}


class TestDeleteLabel:
    async def test_delete_label(self, client: AsyncClient, sample_issue: Issue) -> None:
        create_resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels",
            json={"name": "backend"},
        )
        label_id = create_resp.json()["id"]
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels/{label_id}"
        )
        assert resp.status_code == 204

        list_resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/labels")
        assert list_resp.json() == []

    async def test_delete_nonexistent_label_returns_404(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/labels/{fake_id}"
        )
        assert resp.status_code == 404
