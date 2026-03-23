import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.dependencies import get_session
from personal_jira.models.issue import Issue
from personal_jira.schemas.issue import CloneRequest, IssueCreate, IssueResponse
from personal_jira.services.template import TemplateService

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=IssueResponse)
async def create_issue(
    payload: IssueCreate, session: AsyncSession = Depends(get_session)
) -> Issue:
    if payload.parent_id:
        parent = await session.get(Issue, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent issue not found")
    issue = Issue(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        parent_id=payload.parent_id,
    )
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return issue


@router.post("/{issue_id}/clone", status_code=status.HTTP_201_CREATED, response_model=IssueResponse)
async def clone_issue(
    issue_id: uuid.UUID,
    payload: CloneRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> Issue:
    svc = TemplateService(session)
    title_override = payload.title_override if payload else None
    clone = await svc.clone_issue(issue_id, title_override)
    if not clone:
        raise HTTPException(status_code=404, detail="Issue not found")
    return clone
