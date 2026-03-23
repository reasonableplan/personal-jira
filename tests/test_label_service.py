import uuid
from unittest.mock import MagicMock

import pytest

from personal_jira.services.label import LabelService


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(mock_db: MagicMock) -> LabelService:
    return LabelService(mock_db)


@pytest.fixture
def issue_id() -> uuid.UUID:
    return uuid.uuid4()


class TestAddLabels:
    def test_add_to_empty_labels(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = []
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.add_labels(issue_id, ["bug", "urgent"])

        assert result == ["bug", "urgent"]
        mock_db.commit.assert_called_once()

    def test_add_to_existing_labels(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = ["backend"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.add_labels(issue_id, ["bug"])

        assert sorted(result) == ["backend", "bug"]
        mock_db.commit.assert_called_once()

    def test_add_duplicate_label_ignored(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = ["bug"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.add_labels(issue_id, ["bug"])

        assert result == ["bug"]
        mock_db.commit.assert_called_once()

    def test_add_labels_issue_not_found(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.add_labels(issue_id, ["bug"])

        assert result is None
        mock_db.commit.assert_not_called()


class TestRemoveLabels:
    def test_remove_existing_label(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = ["bug", "urgent", "backend"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.remove_labels(issue_id, ["bug", "urgent"])

        assert result == ["backend"]
        mock_db.commit.assert_called_once()

    def test_remove_nonexistent_label_ignored(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = ["bug"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.remove_labels(issue_id, ["nonexistent"])

        assert result == ["bug"]
        mock_db.commit.assert_called_once()

    def test_remove_labels_issue_not_found(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.remove_labels(issue_id, ["bug"])

        assert result is None
        mock_db.commit.assert_not_called()


class TestGetLabels:
    def test_get_labels_success(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = ["bug", "urgent"]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.get_labels(issue_id)

        assert result == ["bug", "urgent"]

    def test_get_labels_empty(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_issue = MagicMock()
        mock_issue.labels = []
        mock_db.query.return_value.filter.return_value.first.return_value = mock_issue

        result = service.get_labels(issue_id)

        assert result == []

    def test_get_labels_issue_not_found(
        self, service: LabelService, mock_db: MagicMock, issue_id: uuid.UUID,
    ) -> None:
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.get_labels(issue_id)

        assert result is None


class TestGetAllLabels:
    def test_get_all_labels(
        self, service: LabelService, mock_db: MagicMock,
    ) -> None:
        mock_db.query.return_value.filter.return_value.all.return_value = [
            MagicMock(labels=["bug", "urgent"]),
            MagicMock(labels=["bug", "backend"]),
            MagicMock(labels=["frontend"]),
        ]

        result = service.get_all_labels()

        assert result == ["backend", "bug", "frontend", "urgent"]

    def test_get_all_labels_empty(
        self, service: LabelService, mock_db: MagicMock,
    ) -> None:
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = service.get_all_labels()

        assert result == []
