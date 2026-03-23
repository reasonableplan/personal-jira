import uuid
from typing import Optional

from pydantic import BaseModel, Field


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: str = "medium"
    parent_id: Optional[uuid.UUID] = None


class IssueResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    priority: str
    status: str
    parent_id: Optional[uuid.UUID]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class CloneRequest(BaseModel):
    title_override: Optional[str] = None
