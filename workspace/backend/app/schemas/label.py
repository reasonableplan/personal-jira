from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LabelCreate(BaseModel):
    name: str
    color: str


class LabelUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class LabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color: str
    created_at: datetime
