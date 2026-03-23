import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from personal_jira.api.labels import router
from personal_jira.schemas.label import LabelAddRequest, LabelRemoveRequest, LabelListResponse


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(router, prefix="/api/v1")
    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def issue_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


class TestLabelAddSchema:
    def test_valid_labels(self) -> None:
        req = LabelAddRequest(labels=["bug", "urgent"])
        assert req.labels == ["bug", "urgent"]

    def test_empty_labels_rejected(self) -> None:
        with pytest.raises(Exception):
            LabelAddRequest(labels=[])

    def test_duplicate_labels_deduplicated(self) -> None:
        req = LabelAddRequest(labels=["bug", "bug", "urgent"])
        assert req.labels == ["bug", "urgent"]

    def test_whitespace_stripped(self) -> None:
        req = LabelAddRequest(labels=[" bug ", " urgent"])
        assert req.labels == ["bug", "urgent"]

    def test_empty_string_label_rejected(self) -> None:
        with pytest.raises(Exception):
            LabelAddRequest(labels=[""])


class TestLabelRemoveSchema:
    def test_valid_labels(self) -> None:
        req = LabelRemoveRequest(labels=["bug"])
        assert req.labels == ["bug"]

    def test_empty_labels_rejected(self) -> None:
        with pytest.raises(Exception):
            LabelRemoveRequest(labels=[])


class TestLabelListResponse:
    def test_response_structure(self) -> None:
        resp = LabelListResponse(labels=["bug", "feature"], count=2)
        assert resp.labels == ["bug", "feature"]
        assert resp.count == 2


class TestAddLabelsEndpoint:
    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_add_labels_success(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.add_labels.return_value = ["bug", "urgent", "backend"]

        response = client.post(
            f"/api/v1/issues/{issue_id}/labels",
            json={"labels": ["bug", "urgent"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["bug", "urgent", "backend"]
        assert data["count"] == 3
        mock_service.add_labels.assert_called_once_with(issue_id, ["bug", "urgent"])

    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_add_labels_issue_not_found(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.add_labels.return_value = None

        response = client.post(
            f"/api/v1/issues/{issue_id}/labels",
            json={"labels": ["bug"]},
        )

        assert response.status_code == 404

    def test_add_labels_invalid_body(self, client: TestClient, issue_id: uuid.UUID) -> None:
        response = client.post(
            f"/api/v1/issues/{issue_id}/labels",
            json={"labels": []},
        )
        assert response.status_code == 422

    def test_add_labels_invalid_uuid(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/issues/not-a-uuid/labels",
            json={"labels": ["bug"]},
        )
        assert response.status_code == 422


class TestRemoveLabelsEndpoint:
    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_remove_labels_success(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.remove_labels.return_value = ["backend"]

        response = client.request(
            "DELETE",
            f"/api/v1/issues/{issue_id}/labels",
            json={"labels": ["bug"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["backend"]
        assert data["count"] == 1
        mock_service.remove_labels.assert_called_once_with(issue_id, ["bug"])

    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_remove_labels_issue_not_found(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.remove_labels.return_value = None

        response = client.request(
            "DELETE",
            f"/api/v1/issues/{issue_id}/labels",
            json={"labels": ["bug"]},
        )

        assert response.status_code == 404


class TestGetLabelsEndpoint:
    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_get_labels_success(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.get_labels.return_value = ["bug", "urgent"]

        response = client.get(f"/api/v1/issues/{issue_id}/labels")

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["bug", "urgent"]
        assert data["count"] == 2
        mock_service.get_labels.assert_called_once_with(issue_id)

    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_get_labels_issue_not_found(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient, issue_id: uuid.UUID,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.get_labels.return_value = None

        response = client.get(f"/api/v1/issues/{issue_id}/labels")

        assert response.status_code == 404


class TestGetAllLabelsEndpoint:
    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_get_all_labels(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.get_all_labels.return_value = ["backend", "bug", "frontend", "urgent"]

        response = client.get("/api/v1/labels")

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == ["backend", "bug", "frontend", "urgent"]
        assert data["count"] == 4

    @patch("personal_jira.api.labels.LabelService")
    @patch("personal_jira.api.labels.get_db")
    def test_get_all_labels_empty(
        self, mock_get_db: MagicMock, mock_service_cls: MagicMock,
        client: TestClient,
    ) -> None:
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        mock_service = mock_service_cls.return_value
        mock_service.get_all_labels.return_value = []

        response = client.get("/api/v1/labels")

        assert response.status_code == 200
        data = response.json()
        assert data["labels"] == []
        assert data["count"] == 0
