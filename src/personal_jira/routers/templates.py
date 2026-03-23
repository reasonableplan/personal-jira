import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.dependencies import get_session
from personal_jira.schemas.issue import IssueResponse
from personal_jira.schemas.template import TemplateCreate, TemplateIssueCreate, TemplateResponse
from personal_jira.services.template import DuplicateTemplateNameError, TemplateService

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


def _to_response(tmpl: "IssueTemplate") -> dict:  # type: ignore[name-defined]
    return {
        "id": str(tmpl.id),
        "name": tmpl.name,
        "title_pattern": tmpl.title_pattern,
        "description": tmpl.description,
        "priority": tmpl.priority,
        "labels": json.loads(tmpl.labels),
        "created_at": str(tmpl.created_at),
        "updated_at": str(tmpl.updated_at),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    svc = TemplateService(session)
    try:
        tmpl = await svc.create(
            name=payload.name,
            title_pattern=payload.title_pattern,
            description=payload.description,
            priority=payload.priority,
            labels=payload.labels,
        )
    except DuplicateTemplateNameError:
        raise HTTPException(status_code=409, detail="Template name already exists")
    return _to_response(tmpl)


@router.get("", response_model=list[TemplateResponse])
async def list_templates(session: AsyncSession = Depends(get_session)) -> list[dict]:
    svc = TemplateService(session)
    templates = await svc.list_all()
    return [_to_response(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> dict:
    svc = TemplateService(session)
    tmpl = await svc.get(template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return _to_response(tmpl)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> None:
    svc = TemplateService(session)
    deleted = await svc.delete(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")


@router.post("/{template_id}/issues", status_code=status.HTTP_201_CREATED, response_model=IssueResponse)
async def create_issue_from_template(
    template_id: uuid.UUID,
    payload: TemplateIssueCreate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    svc = TemplateService(session)
    issue = await svc.create_issue_from_template(template_id, payload.summary)
    if not issue:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": str(issue.id),
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "status": issue.status,
        "parent_id": str(issue.parent_id) if issue.parent_id else None,
        "created_at": str(issue.created_at),
        "updated_at": str(issue.updated_at),
    }
