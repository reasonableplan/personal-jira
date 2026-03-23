from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(StrEnum):
    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    ISSUE_DELETED = "issue_deleted"
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_STATUS_CHANGED = "issue_status_changed"


class IssueEvent(BaseModel):
    type: EventType
    issue_id: UUID
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_broadcast_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "issue_id": str(self.issue_id),
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
