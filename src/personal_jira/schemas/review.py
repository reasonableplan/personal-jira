import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from personal_jira.models.issue import IssueStatus
from personal_jira.models.review import ReviewDecision


class ReviewCreate(BaseModel):
    decision: ReviewDecision
    comment: str | None = None
    reviewer: str


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    issue_id: uuid.UUID
    decision: ReviewDecision
    comment: str | None
    reviewer: str
    created_at: datetime
    resulting_status: IssueStatus
