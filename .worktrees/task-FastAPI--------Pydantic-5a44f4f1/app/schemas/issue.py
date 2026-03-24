from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class IssueStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class IssuePriority(StrEnum):
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


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
