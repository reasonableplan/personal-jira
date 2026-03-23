import uuid
from datetime import datetime

from pydantic import BaseModel


class DependencyCreate(BaseModel):
    blocker_issue_id: uuid.UUID


class DependencyResponse(BaseModel):
    id: uuid.UUID
    blocked_issue_id: uuid.UUID
    blocker_issue_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DependencyListResponse(BaseModel):
    blockers: list[DependencyResponse]
    blocks: list[DependencyResponse]
