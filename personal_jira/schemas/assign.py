from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, field_validator


class AssignRequest(BaseModel):
    assignee_id: Optional[str] = None

    @field_validator("assignee_id")
    @classmethod
    def validate_assignee_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            uuid.UUID(v)
        return v


class AssignResponse(BaseModel):
    id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None
    message: str

    model_config = {"from_attributes": True}
