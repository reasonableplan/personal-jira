import pytest
from pydantic import ValidationError

from personal_jira.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
)


class TestIssueCreate:
    def test_minimal_fields(self):
        schema = IssueCreate(title="Test issue", issue_type="Task")
        assert schema.title == "Test issue"
        assert schema.issue_type == "Task"
        assert schema.priority == "Medium"
        assert schema.description is None
        assert schema.assignee is None
        assert schema.labels == []

    def test_all_fields(self):
        schema = IssueCreate(
            title="Full issue",
            description="desc",
            issue_type="Epic",
            priority="High",
            assignee="user1",
            parent_id="00000000-0000-0000-0000-000000000001",
            labels=["backend", "urgent"],
        )
        assert schema.priority == "High"
        assert schema.labels == ["backend", "urgent"]

    def test_title_required(self):
        with pytest.raises(ValidationError):
            IssueCreate(issue_type="Task")

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            IssueCreate(title="", issue_type="Task")

    def test_title_max_length(self):
        with pytest.raises(ValidationError):
            IssueCreate(title="x" * 501, issue_type="Task")

    def test_invalid_priority_rejected(self):
        with pytest.raises(ValidationError):
            IssueCreate(title="t", issue_type="Task", priority="Invalid")

    def test_invalid_issue_type_rejected(self):
        with pytest.raises(ValidationError):
            IssueCreate(title="t", issue_type="Invalid")


class TestIssueUpdate:
    def test_all_optional(self):
        schema = IssueUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}

    def test_partial_update(self):
        schema = IssueUpdate(title="new title")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"title": "new title"}

    def test_multiple_fields(self):
        schema = IssueUpdate(title="new", priority="High", description="desc")
        data = schema.model_dump(exclude_unset=True)
        assert len(data) == 3

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            IssueUpdate(status="Invalid")

    def test_invalid_priority_rejected(self):
        with pytest.raises(ValidationError):
            IssueUpdate(priority="Invalid")


class TestIssueResponse:
    def test_from_attributes(self):
        assert IssueResponse.model_config.get("from_attributes") is True


class TestIssueListResponse:
    def test_structure(self):
        resp = IssueListResponse(items=[], total=0, offset=0, limit=20)
        assert resp.items == []
        assert resp.total == 0
