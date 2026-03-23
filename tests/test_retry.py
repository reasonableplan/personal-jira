import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from src.personal_jira.constants import MAX_RETRY_COUNT
from src.personal_jira.models.issue import Issue, IssueStatus
from src.personal_jira.schemas.retry import RetryRequest, RetryResponse
from src.personal_jira.services.retry import RetryService


class TestRetryConstants:
    def test_max_retry_count_value(self) -> None:
        assert MAX_RETRY_COUNT == 5

    def test_max_retry_count_is_positive(self) -> None:
        assert MAX_RETRY_COUNT > 0


class TestRetryRequest:
    def test_valid_request(self) -> None:
        req = RetryRequest(last_error="Connection timeout")
        assert req.last_error == "Connection timeout"

    def test_request_without_error(self) -> None:
        req = RetryRequest()
        assert req.last_error is None

    def test_request_with_empty_error(self) -> None:
        req = RetryRequest(last_error="")
        assert req.last_error == ""


class TestRetryResponse:
    def test_response_fields(self) -> None:
        issue_id = uuid.uuid4()
        resp = RetryResponse(
            id=issue_id,
            retry_count=3,
            last_error="timeout",
            status=IssueStatus.READY,
        )
        assert resp.id == issue_id
        assert resp.retry_count == 3
        assert resp.last_error == "timeout"
        assert resp.status == IssueStatus.READY

    def test_response_abandoned_status(self) -> None:
        issue_id = uuid.uuid4()
        resp = RetryResponse(
            id=issue_id,
            retry_count=MAX_RETRY_COUNT,
            last_error="fatal error",
            status=IssueStatus.ABANDONED,
        )
        assert resp.status == IssueStatus.ABANDONED


class TestRetryService:
    def setup_method(self) -> None:
        self.db = MagicMock()
        self.service = RetryService(self.db)

    def _make_issue(
        self,
        status: str = IssueStatus.FAILED,
        retry_count: int = 0,
        last_error: str | None = None,
    ) -> Issue:
        issue = MagicMock(spec=Issue)
        issue.id = uuid.uuid4()
        issue.status = status
        issue.retry_count = retry_count
        issue.last_error = last_error
        return issue

    def test_retry_increments_count(self) -> None:
        issue = self._make_issue(retry_count=2)
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error=None)

        assert issue.retry_count == 3
        self.db.commit.assert_called_once()

    def test_retry_saves_last_error(self) -> None:
        issue = self._make_issue()
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error="Connection refused")

        assert issue.last_error == "Connection refused"

    def test_retry_resets_status_to_ready(self) -> None:
        issue = self._make_issue(status=IssueStatus.FAILED)
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error=None)

        assert issue.status == IssueStatus.READY

    def test_retry_exceeds_max_sets_abandoned(self) -> None:
        issue = self._make_issue(retry_count=MAX_RETRY_COUNT - 1)
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error="final error")

        assert issue.retry_count == MAX_RETRY_COUNT
        assert issue.status == IssueStatus.ABANDONED

    def test_retry_already_at_max_stays_abandoned(self) -> None:
        issue = self._make_issue(retry_count=MAX_RETRY_COUNT)
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error="over limit")

        assert issue.retry_count == MAX_RETRY_COUNT + 1
        assert issue.status == IssueStatus.ABANDONED

    def test_retry_nonexistent_issue_raises(self) -> None:
        self.db.get.return_value = None
        fake_id = uuid.uuid4()

        with pytest.raises(ValueError, match="not found"):
            self.service.retry_issue(fake_id, last_error=None)

    def test_retry_preserves_previous_error_when_none(self) -> None:
        issue = self._make_issue(last_error="old error")
        self.db.get.return_value = issue

        result = self.service.retry_issue(issue.id, last_error=None)

        assert issue.last_error == "old error"

    def test_retry_db_refresh_called(self) -> None:
        issue = self._make_issue()
        self.db.get.return_value = issue

        self.service.retry_issue(issue.id, last_error=None)

        self.db.refresh.assert_called_once_with(issue)


class TestRetryEndpoint:
    def setup_method(self) -> None:
        from fastapi.testclient import TestClient

        from src.personal_jira.api.v1.endpoints.retry import router

        self.app = self._create_test_app(router)
        self.client = TestClient(self.app)

    def _create_test_app(self, router):
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return app

    @patch("src.personal_jira.api.v1.endpoints.retry.get_db")
    @patch("src.personal_jira.api.v1.endpoints.retry.RetryService")
    def test_retry_success(self, mock_service_cls: MagicMock, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.retry_count = 1
        mock_issue.last_error = "timeout"
        mock_issue.status = IssueStatus.READY
        mock_service.retry_issue.return_value = mock_issue

        response = self.client.post(
            f"/api/v1/issues/{issue_id}/retry",
            json={"last_error": "timeout"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["retry_count"] == 1
        assert data["last_error"] == "timeout"
        assert data["status"] == IssueStatus.READY

    @patch("src.personal_jira.api.v1.endpoints.retry.get_db")
    @patch("src.personal_jira.api.v1.endpoints.retry.RetryService")
    def test_retry_not_found(self, mock_service_cls: MagicMock, mock_get_db: MagicMock) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.retry_issue.side_effect = ValueError("Issue not found")

        fake_id = uuid.uuid4()
        response = self.client.post(f"/api/v1/issues/{fake_id}/retry")

        assert response.status_code == 404

    @patch("src.personal_jira.api.v1.endpoints.retry.get_db")
    @patch("src.personal_jira.api.v1.endpoints.retry.RetryService")
    def test_retry_abandoned_response(self, mock_service_cls: MagicMock, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.retry_count = MAX_RETRY_COUNT
        mock_issue.last_error = "fatal"
        mock_issue.status = IssueStatus.ABANDONED
        mock_service.retry_issue.return_value = mock_issue

        response = self.client.post(
            f"/api/v1/issues/{issue_id}/retry",
            json={"last_error": "fatal"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == IssueStatus.ABANDONED

    def test_retry_invalid_uuid(self) -> None:
        response = self.client.post("/api/v1/issues/not-a-uuid/retry")
        assert response.status_code == 422

    @patch("src.personal_jira.api.v1.endpoints.retry.get_db")
    @patch("src.personal_jira.api.v1.endpoints.retry.RetryService")
    def test_retry_without_body(self, mock_service_cls: MagicMock, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.retry_count = 1
        mock_issue.last_error = None
        mock_issue.status = IssueStatus.READY
        mock_service.retry_issue.return_value = mock_issue

        response = self.client.post(f"/api/v1/issues/{issue_id}/retry")

        assert response.status_code == 200
        data = response.json()
        assert data["last_error"] is None

    @patch("src.personal_jira.api.v1.endpoints.retry.get_db")
    @patch("src.personal_jira.api.v1.endpoints.retry.RetryService")
    def test_retry_db_rollback_on_error(self, mock_service_cls: MagicMock, mock_get_db: MagicMock) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.retry_issue.side_effect = RuntimeError("DB error")

        issue_id = uuid.uuid4()
        response = self.client.post(
            f"/api/v1/issues/{issue_id}/retry",
            json={"last_error": "err"},
        )

        assert response.status_code == 500
