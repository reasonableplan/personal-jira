from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.issue import (
    IssueCreate,
    IssueListResponse,
    IssuePriority,
    IssueResponse,
    IssueStatus,
    IssueUpdate,
)


def test_issue_status_values():
    assert IssueStatus.TODO == "todo"
    assert IssueStatus.IN_PROGRESS == "in_progress"
    assert IssueStatus.DONE == "done"


def test_issue_priority_values():
    assert IssuePriority.LOW == "low"
    assert IssuePriority.MEDIUM == "medium"
    assert IssuePriority.HIGH == "high"
    assert IssuePriority.CRITICAL == "critical"


def test_issue_create_minimal():
    schema = IssueCreate(title="Test issue")
    assert schema.title == "Test issue"
    assert schema.description is None
    assert schema.priority == IssuePriority.MEDIUM


def test_issue_create_full():
    schema = IssueCreate(
        title="Bug fix",
        description="Fix the login bug",
        priority=IssuePriority.HIGH,
    )
    assert schema.title == "Bug fix"
    assert schema.description == "Fix the login bug"
    assert schema.priority == IssuePriority.HIGH


def test_issue_create_title_required():
    with pytest.raises(ValidationError):
        IssueCreate()


def test_issue_update_all_optional():
    schema = IssueUpdate()
    assert schema.title is None
    assert schema.description is None
    assert schema.priority is None


def test_issue_update_partial():
    schema = IssueUpdate(title="Updated title", priority=IssuePriority.CRITICAL)
    assert schema.title == "Updated title"
    assert schema.description is None
    assert schema.priority == IssuePriority.CRITICAL


def test_issue_response_from_attributes():
    now = datetime.now()
    data = {
        "id": 1,
        "title": "Test",
        "description": None,
        "status": IssueStatus.TODO,
        "priority": IssuePriority.MEDIUM,
        "created_at": now,
        "updated_at": now,
    }
    schema = IssueResponse(**data)
    assert schema.id == 1
    assert schema.title == "Test"
    assert schema.status == IssueStatus.TODO
    assert schema.model_config.get("from_attributes") is True


def test_issue_list_response():
    now = datetime.now()
    item = IssueResponse(
        id=1,
        title="Test",
        description=None,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
        created_at=now,
        updated_at=now,
    )
    response = IssueListResponse(items=[item], total=1)
    assert len(response.items) == 1
    assert response.total == 1


def test_issue_list_response_empty():
    response = IssueListResponse(items=[], total=0)
    assert response.items == []
    assert response.total == 0
