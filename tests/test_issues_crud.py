import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssuePriority, IssueStatus, IssueType

API_PREFIX = "/api/v1/issues"


@pytest.fixture
async def sample_issue_data() -> dict:
    return {
        "title": "Test issue",
        "description": "Test description",
        "issue_type": IssueType.TASK.value,
        "priority": IssuePriority.MEDIUM.value,
    }


@pytest.fixture
async def created_issue(client: AsyncClient, sample_issue_data: dict) -> dict:
    resp = await client.post(API_PREFIX, json=sample_issue_data)
    assert resp.status_code == 201
    return resp.json()


class TestCreateIssue:
    async def test_create_minimal(self, client: AsyncClient) -> None:
        payload = {"title": "Minimal issue", "issue_type": IssueType.TASK.value}
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Minimal issue"
        assert data["issue_type"] == IssueType.TASK.value
        assert data["status"] == IssueStatus.BACKLOG.value
        assert data["priority"] == IssuePriority.MEDIUM.value
        assert "id" in data
        assert "created_at" in data

    async def test_create_full_fields(
        self, client: AsyncClient, sample_issue_data: dict
    ) -> None:
        sample_issue_data["labels"] = ["backend", "urgent"]
        resp = await client.post(API_PREFIX, json=sample_issue_data)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == sample_issue_data["title"]
        assert data["description"] == sample_issue_data["description"]
        assert data["issue_type"] == sample_issue_data["issue_type"]
        assert data["priority"] == sample_issue_data["priority"]

    async def test_create_with_parent(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        child_payload = {
            "title": "Child issue",
            "issue_type": IssueType.SUBTASK.value,
            "parent_id": created_issue["id"],
        }
        resp = await client.post(API_PREFIX, json=child_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["parent_id"] == created_issue["id"]

    async def test_create_invalid_parent_returns_404(
        self, client: AsyncClient
    ) -> None:
        payload = {
            "title": "Orphan",
            "issue_type": IssueType.TASK.value,
            "parent_id": str(uuid.uuid4()),
        }
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 404

    async def test_create_missing_title_returns_422(
        self, client: AsyncClient
    ) -> None:
        payload = {"issue_type": IssueType.TASK.value}
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 422

    async def test_create_empty_title_returns_422(
        self, client: AsyncClient
    ) -> None:
        payload = {"title": "", "issue_type": IssueType.TASK.value}
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 422

    async def test_create_whitespace_title_returns_422(
        self, client: AsyncClient
    ) -> None:
        payload = {"title": "   ", "issue_type": IssueType.TASK.value}
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 422

    async def test_create_default_priority(
        self, client: AsyncClient
    ) -> None:
        payload = {"title": "No priority", "issue_type": IssueType.BUG.value}
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 201
        assert resp.json()["priority"] == IssuePriority.MEDIUM.value

    async def test_create_generates_unique_id(
        self, client: AsyncClient
    ) -> None:
        payload = {"title": "Issue A", "issue_type": IssueType.TASK.value}
        resp1 = await client.post(API_PREFIX, json=payload)
        resp2 = await client.post(API_PREFIX, json=payload)
        assert resp1.json()["id"] != resp2.json()["id"]

    async def test_create_all_issue_types(
        self, client: AsyncClient
    ) -> None:
        for issue_type in IssueType:
            payload = {"title": f"Type {issue_type.value}", "issue_type": issue_type.value}
            resp = await client.post(API_PREFIX, json=payload)
            assert resp.status_code == 201
            assert resp.json()["issue_type"] == issue_type.value

    async def test_create_all_priorities(
        self, client: AsyncClient
    ) -> None:
        for priority in IssuePriority:
            payload = {
                "title": f"Priority {priority.value}",
                "issue_type": IssueType.TASK.value,
                "priority": priority.value,
            }
            resp = await client.post(API_PREFIX, json=payload)
            assert resp.status_code == 201
            assert resp.json()["priority"] == priority.value


class TestGetIssueList:
    async def test_list_empty(self, client: AsyncClient) -> None:
        resp = await client.get(API_PREFIX)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_returns_created_issues(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.get(API_PREFIX)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        ids = [item["id"] for item in data["items"]]
        assert created_issue["id"] in ids

    async def test_list_pagination_offset_limit(
        self, client: AsyncClient
    ) -> None:
        for i in range(5):
            await client.post(
                API_PREFIX,
                json={"title": f"Issue {i}", "issue_type": IssueType.TASK.value},
            )
        resp = await client.get(API_PREFIX, params={"offset": 0, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    async def test_list_pagination_second_page(
        self, client: AsyncClient
    ) -> None:
        for i in range(5):
            await client.post(
                API_PREFIX,
                json={"title": f"Issue {i}", "issue_type": IssueType.TASK.value},
            )
        resp = await client.get(API_PREFIX, params={"offset": 2, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

    async def test_list_excludes_soft_deleted(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        resp = await client.get(API_PREFIX)
        assert resp.status_code == 200
        ids = [item["id"] for item in resp.json()["items"]]
        assert created_issue["id"] not in ids


class TestGetIssueDetail:
    async def test_get_by_id(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.get(f"{API_PREFIX}/{created_issue['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == created_issue["id"]
        assert data["title"] == created_issue["title"]

    async def test_get_includes_children(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        child_payload = {
            "title": "Child",
            "issue_type": IssueType.SUBTASK.value,
            "parent_id": created_issue["id"],
        }
        child_resp = await client.post(API_PREFIX, json=child_payload)
        assert child_resp.status_code == 201

        resp = await client.get(f"{API_PREFIX}/{created_issue['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert "children" in data
        assert len(data["children"]) == 1
        assert data["children"][0]["title"] == "Child"

    async def test_get_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"{API_PREFIX}/{fake_id}")
        assert resp.status_code == 404

    async def test_get_invalid_uuid_returns_422(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get(f"{API_PREFIX}/not-a-uuid")
        assert resp.status_code == 422


class TestUpdateIssue:
    async def test_update_title(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"title": "Updated title"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"

    async def test_update_description(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"description": "New description"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "New description"

    async def test_update_priority(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"priority": IssuePriority.CRITICAL.value},
        )
        assert resp.status_code == 200
        assert resp.json()["priority"] == IssuePriority.CRITICAL.value

    async def test_update_status(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"status": IssueStatus.TODO.value},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == IssueStatus.TODO.value

    async def test_update_multiple_fields(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={
                "title": "Multi update",
                "priority": IssuePriority.HIGH.value,
                "description": "Updated desc",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Multi update"
        assert data["priority"] == IssuePriority.HIGH.value
        assert data["description"] == "Updated desc"

    async def test_update_preserves_unmodified_fields(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        original_type = created_issue["issue_type"]
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"title": "Only title changed"},
        )
        assert resp.status_code == 200
        assert resp.json()["issue_type"] == original_type

    async def test_update_sets_updated_at(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}",
            json={"title": "Trigger updated_at"},
        )
        assert resp.status_code == 200
        assert resp.json()["updated_at"] is not None

    async def test_update_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = str(uuid.uuid4())
        resp = await client.patch(
            f"{API_PREFIX}/{fake_id}", json={"title": "Ghost"}
        )
        assert resp.status_code == 404

    async def test_update_empty_title_returns_422(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.patch(
            f"{API_PREFIX}/{created_issue['id']}", json={"title": ""}
        )
        assert resp.status_code == 422


class TestDeleteIssue:
    async def test_soft_delete(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        assert resp.status_code == 200
        get_resp = await client.get(f"{API_PREFIX}/{created_issue['id']}")
        assert get_resp.status_code == 404

    async def test_hard_delete(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.delete(
            f"{API_PREFIX}/{created_issue['id']}", params={"hard": True}
        )
        assert resp.status_code == 200

    async def test_delete_nonexistent_returns_404(
        self, client: AsyncClient
    ) -> None:
        fake_id = str(uuid.uuid4())
        resp = await client.delete(f"{API_PREFIX}/{fake_id}")
        assert resp.status_code == 404

    async def test_delete_with_children_returns_409(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        child_payload = {
            "title": "Child blocker",
            "issue_type": IssueType.SUBTASK.value,
            "parent_id": created_issue["id"],
        }
        await client.post(API_PREFIX, json=child_payload)
        resp = await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        assert resp.status_code == 409

    async def test_soft_delete_then_list_excludes(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        resp = await client.get(API_PREFIX)
        ids = [item["id"] for item in resp.json()["items"]]
        assert created_issue["id"] not in ids

    async def test_hard_delete_cascades_comments(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        resp = await client.delete(
            f"{API_PREFIX}/{created_issue['id']}", params={"hard": True}
        )
        assert resp.status_code == 200
        get_resp = await client.get(f"{API_PREFIX}/{created_issue['id']}")
        assert get_resp.status_code == 404

    async def test_delete_idempotent_soft(
        self, client: AsyncClient, created_issue: dict
    ) -> None:
        await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        resp = await client.delete(f"{API_PREFIX}/{created_issue['id']}")
        assert resp.status_code == 404
