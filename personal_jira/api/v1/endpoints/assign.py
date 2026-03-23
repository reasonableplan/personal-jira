from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.exceptions import IssueNotFoundError
from personal_jira.schemas.assign import AssignRequest, AssignResponse
from personal_jira.services.assign import AssignService

router = APIRouter()


@router.patch("/issues/{issue_id}/assign", response_model=AssignResponse)
def assign_issue(
    issue_id: uuid.UUID,
    body: AssignRequest,
    db: Session = Depends(get_db),
) -> AssignResponse:
    service = AssignService(db)
    assignee_uuid = uuid.UUID(body.assignee_id) if body.assignee_id else None

    try:
        issue = service.assign(issue_id, assignee_uuid)
    except IssueNotFoundError:
        raise HTTPException(status_code=404, detail="Issue not found")

    message = "Assignee updated" if issue.assignee_id else "Assignee removed"
    return AssignResponse(
        id=issue.id,
        assignee_id=issue.assignee_id,
        message=message,
    )
