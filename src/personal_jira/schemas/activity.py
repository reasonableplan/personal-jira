import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from personal_jira.models.activity import ActivityType


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    issue_id: uuid.UUID
    activity_type: ActivityType
    actor: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    detail: Optional[str] = None
    created_at: datetime


class ActivityListResponse(BaseModel):
    items: list[ActivityLogResponse]
    total: int
    offset: int
    limit: int
