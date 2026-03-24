import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.issue import IssueStatus
from app.schemas.issue import (
    IssueCreate,
    IssueListResponse,
    IssueResponse,
    IssueUpdate,
    StatusUpdate,
)


def test_issue_create_minimal() -> None:
    schema = IssueCreate(title="Test")
    assert schema.title == "Test"
    assert schema.description is None
    assert schema.priority == 3


def test_issue_create_full() -> None:
    schema = IssueCreate(title="Bug", description="desc", priority=1)
    assert schema.title == "Bug"
    assert schema.description == "desc"
    assert schema.priority == 1


def test_issue_create_empty_title_fails() -> None:
    with pytest.raises(ValidationError):
        IssueCreate(title="")


def test_issue_create_title_too_long_fails() -> None:
    with pytest.raises(ValidationError):
        IssueCreate(title="x" * 201)


def test_issue_create_priority_out_of_range() -> None:
    with pytest.raises(ValidationError):
        IssueCreate(title="T", priority=0)
    with pytest.raises(ValidationError):
        IssueCreate(title="T", priority=6)


def test_issue_update_all_optional() -> None:
    schema = IssueUpdate()
    assert schema.title is None
    assert schema.description is None
    assert schema.status is None
    assert schema.priority is None


def test_issue_update_partial() -> None:
    schema = IssueUpdate(title="Updated", status=IssueStatus.DONE)
    assert schema.title == "Updated"
    assert schema.status == IssueStatus.DONE


def test_status_update_required() -> None:
    schema = StatusUpdate(status=IssueStatus.IN_PROGRESS)
    assert schema.status == IssueStatus.IN_PROGRESS


def test_status_update_missing_fails() -> None:
    with pytest.raises(ValidationError):
        StatusUpdate()


def test_issue_response_from_attributes() -> None:
    now = datetime.utcnow()
    uid = uuid.uuid4()
    data = {
        "id": uid,
        "title": "T",
        "description": None,
        "status": IssueStatus.TODO,
        "priority": 3,
        "created_at": now,
        "updated_at": None,
    }
    resp = IssueResponse.model_validate(data)
    assert resp.id == uid
    assert resp.title == "T"
    assert resp.status == IssueStatus.TODO


def test_issue_list_response() -> None:
    now = datetime.utcnow()
    uid = uuid.uuid4()
    item = IssueResponse(
        id=uid, title="T", description=None,
        status=IssueStatus.TODO, priority=3,
        created_at=now, updated_at=None,
    )
    resp = IssueListResponse(items=[item], total=1)
    assert resp.total == 1
    assert len(resp.items) == 1
