from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.task import TaskResponse


class StoryCreate(BaseModel):
    title: str
    description: str | None = None
    epic_id: UUID


class StoryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    epic_id: UUID | None = None


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    epic_id: UUID
    task_count: int
    completion_rate: float
    created_at: datetime
    updated_at: datetime


class StoryDetailResponse(StoryResponse):
    tasks: list[TaskResponse] = []
