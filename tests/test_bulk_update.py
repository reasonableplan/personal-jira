import uuid
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from personal_jira.schemas.bulk import BulkUpdateRequest, BulkUpdateItem, BulkUpdateResponse, BulkUpdateResultItem
from personal_jira.services.bulk import BulkUpdateService
from personal_jira.constants import BULK_UPDATE_MAX_ITEMS


class TestBulkUpdateConstants:
    def test_max_items_defined(self) -> None:
        assert BULK_UPDATE_MAX_ITEMS == 50


class TestBulkUpdateItem:
    def test_valid_status_update(self) -> None:
        item = BulkUpdateItem(id=uuid.uuid4(), status="In Progress")
        assert item.status == "In Progress"
        assert item.assignee is None
        assert item.labels is None
        assert item.priority is None

    def test_valid_assignee_update(self) -> None:
        item = BulkUpdateItem(id=uuid.uuid4(), assignee="user-1")
        assert item.assignee == "user-1"

    def test_valid_labels_update(self) -> None:
        item = BulkUpdateItem(id=uuid.uuid4(), labels=["bug", "urgent"])
        assert item.labels == ["bug", "urgent"]

    def test_valid_priority_update(self) -> None:
        item = BulkUpdateItem(id=uuid.uuid4(), priority="High")
        assert item.priority == "High"

    def test_valid_multiple_fields(self) -> None:
        item = BulkUpdateItem(
            id=uuid.uuid4(),
            status="Done",
            assignee="user-2",
            labels=["feature"],
            priority="Low",
        )
        assert item.status == "Done"
        assert item.assignee == "user-2"

    def test_no_update_fields_raises(self) -> None:
        with pytest.raises(ValidationError):
            BulkUpdateItem(id=uuid.uuid4())


class TestBulkUpdateRequest:
    def test_valid_request(self) -> None:
        req = BulkUpdateRequest(
            items=[BulkUpdateItem(id=uuid.uuid4(), status="Done")]
        )
        assert len(req.items) == 1

    def test_empty_items_raises(self) -> None:
        with pytest.raises(ValidationError):
            BulkUpdateRequest(items=[])

    def test_exceeds_max_items_raises(self) -> None:
        items = [
            BulkUpdateItem(id=uuid.uuid4(), status="Done")
            for _ in range(BULK_UPDATE_MAX_ITEMS + 1)
        ]
        with pytest.raises(ValidationError):
            BulkUpdateRequest(items=items)

    def test_max_items_accepted(self) -> None:
        items = [
            BulkUpdateItem(id=uuid.uuid4(), status="Done")
            for _ in range(BULK_UPDATE_MAX_ITEMS)
        ]
        req = BulkUpdateRequest(items=items)
        assert len(req.items) == BULK_UPDATE_MAX_ITEMS


class TestBulkUpdateResponse:
    def test_response_structure(self) -> None:
        result = BulkUpdateResultItem(
            id=uuid.uuid4(), success=True, error=None
        )
        resp = BulkUpdateResponse(
            total=1, succeeded=1, failed=0, results=[result]
        )
        assert resp.total == 1
        assert resp.succeeded == 1
        assert resp.failed == 0

    def test_response_with_failure(self) -> None:
        rid = uuid.uuid4()
        result = BulkUpdateResultItem(
            id=rid, success=False, error="Issue not found"
        )
        resp = BulkUpdateResponse(
            total=1, succeeded=0, failed=1, results=[result]
        )
        assert resp.results[0].success is False
        assert resp.results[0].error == "Issue not found"


class TestBulkUpdateService:
    def setup_method(self) -> None:
        self.db = MagicMock()
        self.service = BulkUpdateService(self.db)

    def test_update_existing_issues(self) -> None:
        issue_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None
        self.db.query.return_value.filter.return_value.first.return_value = mock_issue

        items = [BulkUpdateItem(id=issue_id, status="In Progress")]
        result = self.service.bulk_update(items)

        assert result.total == 1
        assert result.succeeded == 1
        assert result.failed == 0
        assert mock_issue.status == "In Progress"
        self.db.commit.assert_called_once()

    def test_update_nonexistent_issue(self) -> None:
        issue_id = uuid.uuid4()
        self.db.query.return_value.filter.return_value.first.return_value = None

        items = [BulkUpdateItem(id=issue_id, status="Done")]
        result = self.service.bulk_update(items)

        assert result.total == 1
        assert result.succeeded == 0
        assert result.failed == 1
        assert result.results[0].error == "Issue not found"

    def test_update_soft_deleted_issue(self) -> None:
        issue_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = "2026-01-01T00:00:00"
        self.db.query.return_value.filter.return_value.first.return_value = mock_issue

        items = [BulkUpdateItem(id=issue_id, status="Done")]
        result = self.service.bulk_update(items)

        assert result.total == 1
        assert result.succeeded == 0
        assert result.failed == 1
        assert "deleted" in result.results[0].error.lower()

    def test_partial_success(self) -> None:
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = id1
        mock_issue.deleted_at = None

        def side_effect(*args, **kwargs):
            query_mock = MagicMock()
            filter_mock = MagicMock()
            self._call_count = getattr(self, "_call_count", 0) + 1
            if self._call_count == 1:
                filter_mock.first.return_value = mock_issue
            else:
                filter_mock.first.return_value = None
            query_mock.filter.return_value = filter_mock
            return query_mock

        self.db.query.side_effect = side_effect

        items = [
            BulkUpdateItem(id=id1, status="Done"),
            BulkUpdateItem(id=id2, assignee="user-1"),
        ]
        result = self.service.bulk_update(items)

        assert result.total == 2
        assert result.succeeded == 1
        assert result.failed == 1

    def test_update_multiple_fields(self) -> None:
        issue_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None
        self.db.query.return_value.filter.return_value.first.return_value = mock_issue

        items = [BulkUpdateItem(
            id=issue_id,
            status="In Progress",
            assignee="user-3",
            labels=["bug"],
            priority="Critical",
        )]
        result = self.service.bulk_update(items)

        assert result.succeeded == 1
        assert mock_issue.status == "In Progress"
        assert mock_issue.assignee == "user-3"
        assert mock_issue.labels == ["bug"]
        assert mock_issue.priority == "Critical"

    def test_rollback_on_commit_error(self) -> None:
        issue_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.deleted_at = None
        self.db.query.return_value.filter.return_value.first.return_value = mock_issue
        self.db.commit.side_effect = Exception("DB error")

        items = [BulkUpdateItem(id=issue_id, status="Done")]
        with pytest.raises(Exception, match="DB error"):
            self.service.bulk_update(items)

        self.db.rollback.assert_called_once()


class TestBulkUpdateEndpoint:
    @pytest.fixture
    def client(self) -> MagicMock:
        from fastapi.testclient import TestClient
        from personal_jira.api.v1.endpoints.bulk import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/issues")
        return TestClient(app)

    def test_bulk_update_success(self, client: MagicMock) -> None:
        issue_id = str(uuid.uuid4())
        with patch("personal_jira.api.v1.endpoints.bulk.BulkUpdateService") as mock_svc_cls:
            mock_svc = MagicMock()
            mock_svc.bulk_update.return_value = BulkUpdateResponse(
                total=1,
                succeeded=1,
                failed=0,
                results=[BulkUpdateResultItem(id=uuid.UUID(issue_id), success=True, error=None)],
            )
            mock_svc_cls.return_value = mock_svc

            resp = client.patch(
                "/api/v1/issues/bulk",
                json={"items": [{"id": issue_id, "status": "Done"}]},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["succeeded"] == 1

    def test_bulk_update_empty_items_422(self, client: MagicMock) -> None:
        resp = client.patch(
            "/api/v1/issues/bulk",
            json={"items": []},
        )
        assert resp.status_code == 422

    def test_bulk_update_invalid_uuid_422(self, client: MagicMock) -> None:
        resp = client.patch(
            "/api/v1/issues/bulk",
            json={"items": [{"id": "not-a-uuid", "status": "Done"}]},
        )
        assert resp.status_code == 422

    def test_bulk_update_no_fields_422(self, client: MagicMock) -> None:
        issue_id = str(uuid.uuid4())
        resp = client.patch(
            "/api/v1/issues/bulk",
            json={"items": [{"id": issue_id}]},
        )
        assert resp.status_code == 422

    def test_bulk_update_exceeds_max_422(self, client: MagicMock) -> None:
        items = [
            {"id": str(uuid.uuid4()), "status": "Done"}
            for _ in range(BULK_UPDATE_MAX_ITEMS + 1)
        ]
        resp = client.patch(
            "/api/v1/issues/bulk",
            json={"items": items},
        )
        assert resp.status_code == 422
