from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

TITLE_MAX_LENGTH = 200
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3


class IssueStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class IssueCreate(BaseModel):
    title: str = Field(max_length=TITLE_MAX_LENGTH)
    description: str | None = None
    priority: int = Field(default=DEFAULT_PRIORITY, ge=MIN_PRIORITY, le=MAX_PRIORITY)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=TITLE_MAX_LENGTH)
    description: str | None = None
    priority: int | None = Field(default=None, ge=MIN_PRIORITY, le=MAX_PRIORITY)


class StatusUpdate(BaseModel):
    status: IssueStatus


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: int
    created_at: datetime
    updated_at: datetime | None


class IssueListResponse(BaseModel):
    items: list[IssueResponse]
    total: int
