import uuid

from pydantic import BaseModel

from src.personal_jira.models.issue import IssueStatus


class RetryRequest(BaseModel):
    last_error: str | None = None


class RetryResponse(BaseModel):
    id: uuid.UUID
    retry_count: int
    last_error: str | None
    status: str

    model_config = {"from_attributes": True}
