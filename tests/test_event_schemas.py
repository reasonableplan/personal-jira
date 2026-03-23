from uuid import uuid4

import pytest

from personal_jira.schemas.events import EventType, IssueEvent


class TestEventType:
    def test_issue_created_value(self) -> None:
        assert EventType.ISSUE_CREATED.value == "issue_created"

    def test_issue_updated_value(self) -> None:
        assert EventType.ISSUE_UPDATED.value == "issue_updated"

    def test_issue_deleted_value(self) -> None:
        assert EventType.ISSUE_DELETED.value == "issue_deleted"

    def test_issue_assigned_value(self) -> None:
        assert EventType.ISSUE_ASSIGNED.value == "issue_assigned"

    def test_issue_status_changed_value(self) -> None:
        assert EventType.ISSUE_STATUS_CHANGED.value == "issue_status_changed"

    def test_all_members(self) -> None:
        assert len(EventType) == 5


class TestIssueEvent:
    def test_create_event(self) -> None:
        issue_id = uuid4()
        event = IssueEvent(
            type=EventType.ISSUE_CREATED,
            issue_id=issue_id,
            data={"title": "Test"},
        )
        assert event.type == EventType.ISSUE_CREATED
        assert event.issue_id == issue_id
        assert event.data == {"title": "Test"}
        assert event.timestamp is not None

    def test_event_to_dict(self) -> None:
        issue_id = uuid4()
        event = IssueEvent(
            type=EventType.ISSUE_CREATED,
            issue_id=issue_id,
        )
        d = event.to_broadcast_dict()
        assert d["type"] == "issue_created"
        assert d["issue_id"] == str(issue_id)
        assert "timestamp" in d
        assert d["data"] == {}

    def test_event_default_data_empty(self) -> None:
        event = IssueEvent(
            type=EventType.ISSUE_UPDATED,
            issue_id=uuid4(),
        )
        assert event.data == {}
