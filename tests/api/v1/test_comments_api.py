import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus, IssueType, IssuePriority

API_PREFIX = "/api/v1"


@pytest.fixture
async def sample_issue(db_session: AsyncSession) -> Issue:
    issue = Issue(
        title="Comment test issue",
        issue_type=IssueType.TASK,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
    )
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


class TestCreateComment:
    async def test_create_comment(self, client: AsyncClient, sample_issue: Issue) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments",
            json={"content": "This is a comment", "author": "user-1"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["content"] == "This is a comment"
        assert data["author"] == "user-1"
        assert "id" in data
        assert "created_at" in data

    async def test_create_comment_nonexistent_issue_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"{API_PREFIX}/issues/{fake_id}/comments",
            json={"content": "orphan comment", "author": "user-1"},
        )
        assert resp.status_code == 404

    async def test_create_comment_empty_content_returns_422(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments",
            json={"content": "", "author": "user-1"},
        )
        assert resp.status_code == 422

    async def test_create_comment_missing_author_returns_422(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments",
            json={"content": "no author"},
        )
        assert resp.status_code == 422


class TestListComments:
    async def test_list_comments_empty(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/comments")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_comments_returns_ordered(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        for i in range(3):
            await client.post(
                f"{API_PREFIX}/issues/{sample_issue.id}/comments",
                json={"content": f"comment-{i}", "author": "user-1"},
            )
        resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/comments")
        assert resp.status_code == 200
        comments = resp.json()
        assert len(comments) == 3
        assert comments[0]["content"] == "comment-0"
        assert comments[2]["content"] == "comment-2"

    async def test_list_comments_nonexistent_issue_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.get(f"{API_PREFIX}/issues/{fake_id}/comments")
        assert resp.status_code == 404


class TestUpdateComment:
    async def test_update_comment(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        create_resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments",
            json={"content": "original", "author": "user-1"},
        )
        comment_id = create_resp.json()["id"]
        resp = await client.patch(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments/{comment_id}",
            json={"content": "updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["content"] == "updated"

    async def test_update_nonexistent_comment_returns_404(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.patch(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments/{fake_id}",
            json={"content": "nope"},
        )
        assert resp.status_code == 404


class TestDeleteComment:
    async def test_delete_comment(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        create_resp = await client.post(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments",
            json={"content": "to delete", "author": "user-1"},
        )
        comment_id = create_resp.json()["id"]
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments/{comment_id}"
        )
        assert resp.status_code == 204

        list_resp = await client.get(f"{API_PREFIX}/issues/{sample_issue.id}/comments")
        assert list_resp.json() == []

    async def test_delete_nonexistent_comment_returns_404(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.delete(
            f"{API_PREFIX}/issues/{sample_issue.id}/comments/{fake_id}"
        )
        assert resp.status_code == 404
