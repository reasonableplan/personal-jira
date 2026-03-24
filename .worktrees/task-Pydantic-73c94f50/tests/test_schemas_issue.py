from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.issue import (
    IssueCreate,
    IssueListResponse,
    IssueResponse,
    IssueStatus,
    IssueUpdate,
    StatusUpdate,
)


def test_issue_status_values() -> None:
    assert IssueStatus.TODO == "todo"
    assert IssueStatus.IN_PROGRESS == "in_progress"
    assert IssueStatus.DONE == "done"


def test_issue_status_invalid() -> None:
    with pytest.raises(ValueError):
        IssueStatus("invalid")


def test_issue_create_minimal() -> None:
    schema = IssueCreate(title="Test")
    assert schema.title == "Test"
    assert schema.description is None
    assert schema.priority == 3


def test_issue_create_full() -> None:
    schema = IssueCreate(title="Test", description="desc", priority=5)
    assert schema.title == "Test"
    assert schema.description == "desc"
    assert schema.priority == 5


def test_issue_create_title_max_length() -> None:
    IssueCreate(title="a" * 200)
    with pytest.raises(ValidationError):
        IssueCreate(title="a" * 201)


def test_issue_create_title_required() -> None:
    with pytest.raises(ValidationError):
        IssueCreate()


def test_issue_create_priority_bounds() -> None:
    IssueCreate(title="t", priority=1)
    IssueCreate(title="t", priority=5)
    with pytest.raises(ValidationError):
        IssueCreate(title="t", priority=0)
    with pytest.raises(ValidationError):
        IssueCreate(title="t", priority=6)


def test_issue_update_all_optional() -> None:
    schema = IssueUpdate()
    assert schema.title is None
    assert schema.description is None
    assert schema.priority is None


def test_issue_update_partial() -> None:
    schema = IssueUpdate(title="New")
    assert schema.title == "New"
    assert schema.description is None


def test_issue_update_title_max_length() -> None:
    with pytest.raises(ValidationError):
        IssueUpdate(title="a" * 201)


def test_issue_update_priority_bounds() -> None:
    with pytest.raises(ValidationError):
        IssueUpdate(priority=0)
    with pytest.raises(ValidationError):
        IssueUpdate(priority=6)


def test_status_update() -> None:
    schema = StatusUpdate(status=IssueStatus.DONE)
    assert schema.status == IssueStatus.DONE


def test_status_update_from_string() -> None:
    schema = StatusUpdate(status="in_progress")
    assert schema.status == IssueStatus.IN_PROGRESS


def test_status_update_invalid() -> None:
    with pytest.raises(ValidationError):
        StatusUpdate(status="invalid")


def test_issue_response_from_attributes() -> None:
    now = datetime(2026, 1, 1, 0, 0, 0)

    class FakeIssue:
        id = 1
        title = "Test"
        description = None
        status = "todo"
        priority = 3
        created_at = now
        updated_at = None

    schema = IssueResponse.model_validate(FakeIssue())
    assert schema.id == 1
    assert schema.title == "Test"
    assert schema.status == IssueStatus.TODO
    assert schema.created_at == now
    assert schema.updated_at is None


def test_issue_list_response() -> None:
    now = datetime(2026, 1, 1, 0, 0, 0)
    item = IssueResponse(
        id=1,
        title="Test",
        description=None,
        status=IssueStatus.TODO,
        priority=3,
        created_at=now,
        updated_at=None,
    )
    schema = IssueListResponse(items=[item], total=1)
    assert len(schema.items) == 1
    assert schema.total == 1
