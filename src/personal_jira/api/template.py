import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.issue import IssueResponse
from personal_jira.schemas.template import (
    CloneIssueRequest,
    CreateFromTemplateRequest,
    TemplateCreate,
    TemplateResponse,
)
from personal_jira.services.template import TemplateService

router = APIRouter(tags=["templates"])
template_service = TemplateService()


@router.post(
    "/api/v1/templates",
    status_code=status.HTTP_201_CREATED,
    response_model=TemplateResponse,
)
async def create_template(
    data: TemplateCreate, db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    template = await template_service.create(db, data)
    return TemplateResponse.model_validate(template)


@router.get("/api/v1/templates", response_model=list[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
) -> list[TemplateResponse]:
    templates = await template_service.list_all(db)
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/api/v1/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> TemplateResponse:
    template = await template_service.get_by_id(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateResponse.model_validate(template)


@router.post(
    "/api/v1/templates/{template_id}/issues",
    status_code=status.HTTP_201_CREATED,
    response_model=IssueResponse,
)
async def create_issue_from_template(
    template_id: uuid.UUID,
    data: CreateFromTemplateRequest,
    db: AsyncSession = Depends(get_db),
) -> IssueResponse:
    try:
        issue = await template_service.create_issue_from_template(
            db, template_id, data.variables
        )
        return IssueResponse.model_validate(issue)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/api/v1/issues/{issue_id}/clone",
    status_code=status.HTTP_201_CREATED,
    response_model=IssueResponse,
)
async def clone_issue(
    issue_id: uuid.UUID,
    data: CloneIssueRequest,
    db: AsyncSession = Depends(get_db),
) -> IssueResponse:
    try:
        issue = await template_service.clone_issue(db, issue_id, data)
        return IssueResponse.model_validate(issue)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
