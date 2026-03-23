import pytest
from uuid import uuid4


class TestCreateIssue:
    def test_create_minimal(self, client):
        resp = client.post("/api/v1/issues", json={
            "title": "Test issue",
            "issue_type": "Task",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test issue"
        assert data["issue_type"] == "Task"
        assert data["status"] == "Backlog"
        assert data["priority"] == "Medium"
        assert "id" in data
        assert "created_at" in data

    def test_create_all_fields(self, client):
        resp = client.post("/api/v1/issues", json={
            "title": "Full issue",
            "description": "A description",
            "issue_type": "Story",
            "priority": "High",
            "assignee": "user1",
            "labels": ["backend"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["description"] == "A description"
        assert data["priority"] == "High"
        assert data["assignee"] == "user1"
        assert data["labels"] == ["backend"]

    def test_create_missing_title_422(self, client):
        resp = client.post("/api/v1/issues", json={"issue_type": "Task"})
        assert resp.status_code == 422

    def test_create_empty_title_422(self, client):
        resp = client.post("/api/v1/issues", json={
            "title": "",
            "issue_type": "Task",
        })
        assert resp.status_code == 422

    def test_create_invalid_priority_422(self, client):
        resp = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
            "priority": "Invalid",
        })
        assert resp.status_code == 422

    def test_create_invalid_type_422(self, client):
        resp = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Invalid",
        })
        assert resp.status_code == 422

    def test_create_with_parent(self, client):
        parent = client.post("/api/v1/issues", json={
            "title": "Parent",
            "issue_type": "Epic",
        }).json()
        resp = client.post("/api/v1/issues", json={
            "title": "Child",
            "issue_type": "Story",
            "parent_id": parent["id"],
        })
        assert resp.status_code == 201
        assert resp.json()["parent_id"] == parent["id"]


class TestGetIssue:
    def test_get_existing(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "Test",
            "issue_type": "Task",
        }).json()
        resp = client.get(f"/api/v1/issues/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]
        assert resp.json()["title"] == "Test"

    def test_get_not_found_404(self, client):
        resp = client.get(f"/api/v1/issues/{uuid4()}")
        assert resp.status_code == 404

    def test_get_invalid_id_422(self, client):
        resp = client.get("/api/v1/issues/not-a-uuid")
        assert resp.status_code == 422


class TestListIssues:
    def test_empty_list(self, client):
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_returns_all(self, client):
        for i in range(3):
            client.post("/api/v1/issues", json={
                "title": f"Issue {i}",
                "issue_type": "Task",
            })
        resp = client.get("/api/v1/issues")
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_pagination_offset(self, client):
        for i in range(5):
            client.post("/api/v1/issues", json={
                "title": f"Issue {i}",
                "issue_type": "Task",
            })
        resp = client.get("/api/v1/issues?offset=2&limit=2")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["offset"] == 2
        assert data["limit"] == 2

    def test_pagination_limit(self, client):
        for i in range(5):
            client.post("/api/v1/issues", json={
                "title": f"Issue {i}",
                "issue_type": "Task",
            })
        resp = client.get("/api/v1/issues?limit=2")
        data = resp.json()
        assert len(data["items"]) == 2

    def test_default_limit(self, client):
        resp = client.get("/api/v1/issues")
        data = resp.json()
        assert data["limit"] == 20

    def test_filter_by_status(self, client):
        client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        })
        resp = client.get("/api/v1/issues?status=Backlog")
        assert resp.json()["total"] == 1
        resp = client.get("/api/v1/issues?status=Done")
        assert resp.json()["total"] == 0

    def test_filter_by_priority(self, client):
        client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
            "priority": "Critical",
        })
        resp = client.get("/api/v1/issues?priority=Critical")
        assert resp.json()["total"] == 1

    def test_filter_by_assignee(self, client):
        client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
            "assignee": "alice",
        })
        resp = client.get("/api/v1/issues?assignee=alice")
        assert resp.json()["total"] == 1
        resp = client.get("/api/v1/issues?assignee=bob")
        assert resp.json()["total"] == 0

    def test_excludes_soft_deleted(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        client.delete(f"/api/v1/issues/{created['id']}")
        resp = client.get("/api/v1/issues")
        assert resp.json()["total"] == 0


class TestUpdateIssue:
    def test_update_single_field(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "Old",
            "issue_type": "Task",
        }).json()
        resp = client.patch(
            f"/api/v1/issues/{created['id']}",
            json={"title": "New"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_update_multiple_fields(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        resp = client.patch(
            f"/api/v1/issues/{created['id']}",
            json={"title": "Updated", "priority": "High", "description": "desc"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated"
        assert data["priority"] == "High"
        assert data["description"] == "desc"

    def test_update_empty_body(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        resp = client.patch(
            f"/api/v1/issues/{created['id']}",
            json={},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "t"

    def test_update_not_found_404(self, client):
        resp = client.patch(
            f"/api/v1/issues/{uuid4()}",
            json={"title": "x"},
        )
        assert resp.status_code == 404

    def test_update_invalid_id_422(self, client):
        resp = client.patch(
            "/api/v1/issues/not-a-uuid",
            json={"title": "x"},
        )
        assert resp.status_code == 422

    def test_update_invalid_status_422(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        resp = client.patch(
            f"/api/v1/issues/{created['id']}",
            json={"status": "Invalid"},
        )
        assert resp.status_code == 422


class TestDeleteIssue:
    def test_soft_delete(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        resp = client.delete(f"/api/v1/issues/{created['id']}")
        assert resp.status_code == 204
        get_resp = client.get(f"/api/v1/issues/{created['id']}")
        assert get_resp.status_code == 404

    def test_hard_delete(self, client):
        created = client.post("/api/v1/issues", json={
            "title": "t",
            "issue_type": "Task",
        }).json()
        resp = client.delete(f"/api/v1/issues/{created['id']}?hard=true")
        assert resp.status_code == 204

    def test_delete_not_found_404(self, client):
        resp = client.delete(f"/api/v1/issues/{uuid4()}")
        assert resp.status_code == 404

    def test_delete_with_children_409(self, client):
        parent = client.post("/api/v1/issues", json={
            "title": "Parent",
            "issue_type": "Epic",
        }).json()
        client.post("/api/v1/issues", json={
            "title": "Child",
            "issue_type": "Story",
            "parent_id": parent["id"],
        })
        resp = client.delete(f"/api/v1/issues/{parent['id']}")
        assert resp.status_code == 409

    def test_delete_invalid_id_422(self, client):
        resp = client.delete("/api/v1/issues/not-a-uuid")
        assert resp.status_code == 422
