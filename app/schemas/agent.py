import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _normalize_skills(skills: list[str]) -> list[str]:
    return sorted(set(s.lower().strip() for s in skills))


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    skills: list[str] = Field(default_factory=list)

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: list[str]) -> list[str]:
        return _normalize_skills(v)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    skills: Optional[list[str]] = None

    @field_validator("skills", mode="before")
    @classmethod
    def normalize_skills(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        return _normalize_skills(v)


class AgentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    skills: list[str]
    status: str
    current_issue_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
