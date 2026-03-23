import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IssueTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    default_title: Optional[str] = None
    default_description: Optional[str] = None
    default_priority: Optional[str] = None
    default_issue_type: Optional[str] = None
    default_labels: list[str] = []


class IssueTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_title: Optional[str] = None
    default_description: Optional[str] = None
    default_priority: Optional[str] = None
    default_issue_type: Optional[str] = None
    default_labels: Optional[list[str]] = None


class IssueTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    default_title: Optional[str] = None
    default_description: Optional[str] = None
    default_priority: Optional[str] = None
    default_issue_type: Optional[str] = None
    default_labels: list[str] = []
    created_at: datetime
    updated_at: datetime


class IssueFromTemplateRequest(BaseModel):
    template_id: uuid.UUID
    title_override: Optional[str] = None
    description_override: Optional[str] = None
    priority_override: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    assignee: Optional[str] = None


class IssueCloneRequest(BaseModel):
    include_comments: bool = True
    include_work_logs: bool = False
    include_children: bool = False
    title_prefix: str = "[CLONE] "


class IssueCloneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_issue_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
