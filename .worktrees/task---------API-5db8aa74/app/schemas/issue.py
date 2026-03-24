from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class IssueStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class IssuePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCreate(BaseModel):
    title: str
    description: str | None = None
    priority: IssuePriority = IssuePriority.MEDIUM


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: IssuePriority | None = None


class StatusUpdate(BaseModel):
    status: IssueStatus


class IssueResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    created_at: datetime
    updated_at: datetime


class IssueListResponse(BaseModel):
    items: list[IssueResponse]
    total: int
