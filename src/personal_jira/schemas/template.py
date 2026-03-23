import uuid
from typing import Optional

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    title_pattern: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: list[str] = Field(default_factory=list)


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    title_pattern: str
    description: Optional[str]
    priority: Optional[str]
    labels: list[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class TemplateIssueCreate(BaseModel):
    summary: str = Field(..., min_length=1)
