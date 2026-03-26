from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.story import StoryResponse


class EpicCreate(BaseModel):
    title: str = Field(max_length=200)
    description: str | None = None


class EpicUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None


class EpicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    story_count: int
    completion_rate: float
    created_at: datetime
    updated_at: datetime


class EpicDetailResponse(EpicResponse):
    stories: list[StoryResponse]
