import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.issue import IssueStatus


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=5)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: IssueStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class StatusUpdate(BaseModel):
    status: IssueStatus


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    status: IssueStatus
    priority: int
    created_at: datetime | None
    updated_at: datetime | None


class IssueListResponse(BaseModel):
    items: list[IssueResponse]
    total: int
