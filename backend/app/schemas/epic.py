from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EpicCreate(BaseModel):
    title: str
    description: str | None = None


class EpicUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class EpicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    epic_id: UUID
    title: str
    description: str | None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class EpicDetailResponse(EpicResponse):
    stories: list[StoryResponse] = []
