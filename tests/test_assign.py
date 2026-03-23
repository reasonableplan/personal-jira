import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from personal_jira.schemas.assign import AssignRequest, AssignResponse
from personal_jira.services.assign import AssignService
from personal_jira.exceptions import IssueNotFoundError


class TestAssignRequest:
    def test_assign_with_assignee_id(self) -> None:
        req = AssignRequest(assignee_id=str(uuid.uuid4()))
        assert req.assignee_id is not None

    def test_assign_with_none_unassigns(self) -> None:
        req = AssignRequest(assignee_id=None)
        assert req.assignee_id is None

    def test_assign_default_is_none(self) -> None:
        req = AssignRequest()
        assert req.assignee_id is None

    def test_assign_invalid_uuid_rejected(self) -> None:
        with pytest.raises(ValueError):
            AssignRequest(assignee_id="not-a-uuid")


class TestAssignResponse:
    def test_response_fields(self) -> None:
        issue_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        resp = AssignResponse(
            id=issue_id,
            assignee_id=assignee_id,
            message="Assignee updated",
        )
        assert resp.id == issue_id
        assert resp.assignee_id == assignee_id
        assert resp.message == "Assignee updated"

    def test_response_unassigned(self) -> None:
        resp = AssignResponse(
            id=uuid.uuid4(),
            assignee_id=None,
            message="Assignee removed",
        )
        assert resp.assignee_id is None


class TestAssignService:
    def setup_method(self) -> None:
        self.db = MagicMock()
        self.service = AssignService(self.db)

    def test_assign_issue_success(self) -> None:
        issue_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = None

        query = self.db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        result = self.service.assign(issue_id, assignee_id)

        assert result.assignee_id == assignee_id
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_issue)

    def test_assign_issue_change_assignee(self) -> None:
        issue_id = uuid.uuid4()
        old_assignee = uuid.uuid4()
        new_assignee = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = old_assignee

        query = self.db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        result = self.service.assign(issue_id, new_assignee)

        assert result.assignee_id == new_assignee
        self.db.commit.assert_called_once()

    def test_unassign_issue(self) -> None:
        issue_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = uuid.uuid4()

        query = self.db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        result = self.service.assign(issue_id, None)

        assert result.assignee_id is None
        self.db.commit.assert_called_once()

    def test_assign_issue_not_found(self) -> None:
        issue_id = uuid.uuid4()
        query = self.db.query.return_value
        query.filter.return_value.first.return_value = None

        with pytest.raises(IssueNotFoundError):
            self.service.assign(issue_id, uuid.uuid4())

        self.db.commit.assert_not_called()

    def test_assign_same_assignee_no_error(self) -> None:
        issue_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = assignee_id

        query = self.db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        result = self.service.assign(issue_id, assignee_id)

        assert result.assignee_id == assignee_id
        self.db.commit.assert_called_once()


class TestAssignEndpoint:
    def setup_method(self) -> None:
        from personal_jira.api.v1.endpoints.assign import router

        self.app = FastAPI()
        self.app.include_router(router, prefix="/api/v1")
        self.client = TestClient(self.app)

    @patch("personal_jira.api.v1.endpoints.assign.get_db")
    def test_assign_success(self, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        assignee_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = None

        query = mock_db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        response = self.client.patch(
            f"/api/v1/issues/{issue_id}/assign",
            json={"assignee_id": str(assignee_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] == str(assignee_id)
        assert data["message"] == "Assignee updated"

    @patch("personal_jira.api.v1.endpoints.assign.get_db")
    def test_unassign_success(self, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        mock_issue = MagicMock()
        mock_issue.id = issue_id
        mock_issue.assignee_id = uuid.uuid4()

        query = mock_db.query.return_value
        query.filter.return_value.first.return_value = mock_issue

        response = self.client.patch(
            f"/api/v1/issues/{issue_id}/assign",
            json={"assignee_id": None},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] is None
        assert data["message"] == "Assignee removed"

    @patch("personal_jira.api.v1.endpoints.assign.get_db")
    def test_assign_not_found_404(self, mock_get_db: MagicMock) -> None:
        issue_id = uuid.uuid4()
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])

        query = mock_db.query.return_value
        query.filter.return_value.first.return_value = None

        response = self.client.patch(
            f"/api/v1/issues/{issue_id}/assign",
            json={"assignee_id": str(uuid.uuid4())},
        )

        assert response.status_code == 404

    def test_assign_invalid_uuid_422(self) -> None:
        response = self.client.patch(
            "/api/v1/issues/not-a-uuid/assign",
            json={"assignee_id": str(uuid.uuid4())},
        )

        assert response.status_code == 422

    @patch("personal_jira.api.v1.endpoints.assign.get_db")
    def test_assign_invalid_assignee_uuid_422(
        self, mock_get_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()

        response = self.client.patch(
            f"/api/v1/issues/{issue_id}/assign",
            json={"assignee_id": "invalid-uuid"},
        )

        assert response.status_code == 422
