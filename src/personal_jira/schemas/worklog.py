import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from personal_jira.constants import WORKLOG_MAX_CONTENT_LENGTH


class WorkLogCreate(BaseModel):
    llm_calls: int = Field(..., ge=0)
    tokens_used: int = Field(..., ge=0)
    content: Optional[str] = Field(None, max_length=WORKLOG_MAX_CONTENT_LENGTH)
    agent_id: Optional[str] = None


class WorkLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    issue_id: uuid.UUID
    agent_id: Optional[str]
    llm_calls: int
    tokens_used: int
    content: Optional[str]
    created_at: datetime
    updated_at: datetime
