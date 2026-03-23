import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from personal_jira.models.issue import Issue, IssueStatus
from tests.conftest import create_issue


class TestCreateDependency:
    def test_create_dependency_success(self, client: TestClient, db: Session) -> None:
        blocked = create_issue(db, "Blocked")
        blocker = create_issue(db, "Blocker")

        resp = client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["blocked_issue_id"] == str(blocked.id)
        assert data["blocker_issue_id"] == str(blocker.id)
        assert "id" in data
        assert "created_at" in data

    def test_create_self_dependency_returns_400(self, client: TestClient, db: Session) -> None:
        issue = create_issue(db, "Self")

        resp = client.post(
            f"/api/v1/issues/{issue.id}/dependencies",
            json={"blocker_issue_id": str(issue.id)},
        )
        assert resp.status_code == 400
        assert "self" in resp.json()["detail"].lower()

    def test_create_duplicate_returns_409(self, client: TestClient, db: Session) -> None:
        blocked = create_issue(db, "Blocked")
        blocker = create_issue(db, "Blocker")

        client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        resp = client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        assert resp.status_code == 409

    def test_create_circular_returns_400(self, client: TestClient, db: Session) -> None:
        issue_a = create_issue(db, "A")
        issue_b = create_issue(db, "B")

        client.post(
            f"/api/v1/issues/{issue_a.id}/dependencies",
            json={"blocker_issue_id": str(issue_b.id)},
        )
        resp = client.post(
            f"/api/v1/issues/{issue_b.id}/dependencies",
            json={"blocker_issue_id": str(issue_a.id)},
        )
        assert resp.status_code == 400
        assert "circular" in resp.json()["detail"].lower()

    def test_create_with_nonexistent_issue_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        blocker = create_issue(db, "Blocker")
        fake_id = uuid.uuid4()

        resp = client.post(
            f"/api/v1/issues/{fake_id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        assert resp.status_code == 404

    def test_create_with_invalid_uuid_returns_422(
        self, client: TestClient, db: Session
    ) -> None:
        resp = client.post(
            "/api/v1/issues/not-a-uuid/dependencies",
            json={"blocker_issue_id": "also-not-uuid"},
        )
        assert resp.status_code == 422


class TestGetDependencies:
    def test_get_dependencies(self, client: TestClient, db: Session) -> None:
        blocked = create_issue(db, "Blocked")
        blocker1 = create_issue(db, "Blocker1")
        blocker2 = create_issue(db, "Blocker2")

        client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker1.id)},
        )
        client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker2.id)},
        )

        resp = client.get(f"/api/v1/issues/{blocked.id}/dependencies")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["blockers"]) == 2
        assert len(data["blocks"]) == 0

    def test_get_dependencies_includes_blocks(
        self, client: TestClient, db: Session
    ) -> None:
        blocker = create_issue(db, "Blocker")
        blocked1 = create_issue(db, "Blocked1")
        blocked2 = create_issue(db, "Blocked2")

        client.post(
            f"/api/v1/issues/{blocked1.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        client.post(
            f"/api/v1/issues/{blocked2.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )

        resp = client.get(f"/api/v1/issues/{blocker.id}/dependencies")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["blockers"]) == 0
        assert len(data["blocks"]) == 2

    def test_get_dependencies_empty(self, client: TestClient, db: Session) -> None:
        issue = create_issue(db, "Alone")
        resp = client.get(f"/api/v1/issues/{issue.id}/dependencies")
        assert resp.status_code == 200
        data = resp.json()
        assert data["blockers"] == []
        assert data["blocks"] == []

    def test_get_dependencies_nonexistent_returns_404(
        self, client: TestClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = client.get(f"/api/v1/issues/{fake_id}/dependencies")
        assert resp.status_code == 404


class TestDeleteDependency:
    def test_delete_dependency(self, client: TestClient, db: Session) -> None:
        blocked = create_issue(db, "Blocked")
        blocker = create_issue(db, "Blocker")

        create_resp = client.post(
            f"/api/v1/issues/{blocked.id}/dependencies",
            json={"blocker_issue_id": str(blocker.id)},
        )
        dep_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/issues/{blocked.id}/dependencies/{dep_id}")
        assert resp.status_code == 204

        get_resp = client.get(f"/api/v1/issues/{blocked.id}/dependencies")
        assert len(get_resp.json()["blockers"]) == 0

    def test_delete_nonexistent_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        issue = create_issue(db, "Issue")
        fake_id = uuid.uuid4()

        resp = client.delete(f"/api/v1/issues/{issue.id}/dependencies/{fake_id}")
        assert resp.status_code == 404
