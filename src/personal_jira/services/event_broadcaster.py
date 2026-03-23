from typing import Any
from uuid import UUID

from personal_jira.schemas.events import EventType, IssueEvent
from personal_jira.services.connection_manager import ConnectionManager


class EventBroadcaster:
    def __init__(self, *, manager: ConnectionManager) -> None:
        self._manager = manager

    async def broadcast_issue_event(
        self,
        *,
        event_type: EventType,
        issue_id: UUID,
        data: dict[str, Any] | None = None,
        exclude: str | None = None,
    ) -> None:
        event = IssueEvent(
            type=event_type,
            issue_id=issue_id,
            data=data or {},
        )
        await self._manager.broadcast(event.to_broadcast_dict(), exclude=exclude)
