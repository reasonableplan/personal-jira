from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.task import TaskResponse


class StoryCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None
    epic_id: UUID


class StoryUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    epic_id: UUID | None = None


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    epic_id: UUID
    task_count: int
    completion_rate: float
    created_at: datetime
    updated_at: datetime


class StoryDetailResponse(StoryResponse):
    tasks: list[TaskResponse]
