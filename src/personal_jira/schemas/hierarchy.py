from __future__ import annotations

from pydantic import BaseModel

from personal_jira.models import IssueType, IssueStatus, IssuePriority


class IssueChildResponse(BaseModel):
    id: int
    title: str
    issue_type: IssueType
    status: IssueStatus
    priority: IssuePriority
    parent_id: int | None = None

    model_config = {"from_attributes": True}


class IssueSubtreeResponse(BaseModel):
    id: int
    title: str
    issue_type: IssueType
    status: IssueStatus
    priority: IssuePriority
    children: list[IssueSubtreeResponse] = []

    model_config = {"from_attributes": True}


class IssueAncestorResponse(BaseModel):
    id: int
    title: str
    issue_type: IssueType
    status: IssueStatus
    priority: IssuePriority

    model_config = {"from_attributes": True}
