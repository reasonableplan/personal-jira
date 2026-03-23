from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from personal_jira.schemas.events import EventType, IssueEvent
from personal_jira.services.event_broadcaster import EventBroadcaster


@pytest.fixture
def mock_manager() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def broadcaster(mock_manager: AsyncMock) -> EventBroadcaster:
    return EventBroadcaster(manager=mock_manager)


class TestEventBroadcaster:
    async def test_broadcast_issue_created(self, broadcaster: EventBroadcaster, mock_manager: AsyncMock) -> None:
        issue_id = uuid4()
        await broadcaster.broadcast_issue_event(
            event_type=EventType.ISSUE_CREATED,
            issue_id=issue_id,
            data={"title": "New bug"},
        )
        mock_manager.broadcast.assert_awaited_once()
        call_arg = mock_manager.broadcast.call_args[0][0]
        assert call_arg["type"] == EventType.ISSUE_CREATED.value
        assert call_arg["issue_id"] == str(issue_id)
        assert call_arg["data"]["title"] == "New bug"

    async def test_broadcast_issue_updated(self, broadcaster: EventBroadcaster, mock_manager: AsyncMock) -> None:
        issue_id = uuid4()
        await broadcaster.broadcast_issue_event(
            event_type=EventType.ISSUE_UPDATED,
            issue_id=issue_id,
            data={"status": "in_progress"},
        )
        call_arg = mock_manager.broadcast.call_args[0][0]
        assert call_arg["type"] == EventType.ISSUE_UPDATED.value

    async def test_broadcast_issue_deleted(self, broadcaster: EventBroadcaster, mock_manager: AsyncMock) -> None:
        issue_id = uuid4()
        await broadcaster.broadcast_issue_event(
            event_type=EventType.ISSUE_DELETED,
            issue_id=issue_id,
        )
        call_arg = mock_manager.broadcast.call_args[0][0]
        assert call_arg["type"] == EventType.ISSUE_DELETED.value
        assert call_arg["data"] == {}

    async def test_broadcast_issue_assigned(self, broadcaster: EventBroadcaster, mock_manager: AsyncMock) -> None:
        issue_id = uuid4()
        await broadcaster.broadcast_issue_event(
            event_type=EventType.ISSUE_ASSIGNED,
            issue_id=issue_id,
            data={"assignee": "agent-1"},
            exclude="agent-1",
        )
        mock_manager.broadcast.assert_awaited_once()
        _, kwargs = mock_manager.broadcast.call_args
        assert kwargs["exclude"] == "agent-1"

    async def test_event_contains_timestamp(self, broadcaster: EventBroadcaster, mock_manager: AsyncMock) -> None:
        await broadcaster.broadcast_issue_event(
            event_type=EventType.ISSUE_CREATED,
            issue_id=uuid4(),
        )
        call_arg = mock_manager.broadcast.call_args[0][0]
        assert "timestamp" in call_arg
