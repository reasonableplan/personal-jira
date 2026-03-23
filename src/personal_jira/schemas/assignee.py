import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AssigneeCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)


class AssigneeResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
