from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus
from app.schemas.label import LabelResponse


class TaskCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.BACKLOG
    priority: int = Field(default=3, ge=1, le=5)
    story_id: UUID
    label_ids: list[UUID] | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    story_id: UUID | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    story_id: UUID
    labels: list[LabelResponse]
    created_at: datetime
    updated_at: datetime
