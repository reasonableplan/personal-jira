from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from personal_jira.config import TITLE_MAX_LENGTH

ISSUE_TYPE_VALUES = Literal["Epic", "Story", "Task", "SubTask"]
ISSUE_STATUS_VALUES = Literal[
    "Backlog", "Ready", "In Progress", "In Review", "Blocked", "Done", "Cancelled"
]
ISSUE_PRIORITY_VALUES = Literal["Critical", "High", "Medium", "Low", "Trivial"]


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=TITLE_MAX_LENGTH)
    description: str | None = None
    issue_type: ISSUE_TYPE_VALUES
    priority: ISSUE_PRIORITY_VALUES = "Medium"
    assignee: str | None = None
    parent_id: uuid.UUID | None = None
    labels: list[str] = Field(default_factory=list)


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LENGTH)
    description: str | None = None
    status: ISSUE_STATUS_VALUES | None = None
    priority: ISSUE_PRIORITY_VALUES | None = None
    assignee: str | None = None
    labels: list[str] | None = None


class IssueResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: str | None
    issue_type: str
    status: str
    priority: str
    assignee: str | None
    parent_id: uuid.UUID | None
    labels: list[str] | None
    created_at: datetime
    updated_at: datetime


class IssueListResponse(BaseModel):
    items: list[IssueResponse]
    total: int
    offset: int
    limit: int
