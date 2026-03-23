import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ClaimRequest(BaseModel):
    agent_id: uuid.UUID


class ClaimResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    status: str
    assignee: Optional[str] = None
    priority: Optional[str] = None
