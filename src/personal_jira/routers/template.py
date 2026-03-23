import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.issue_template import (
    IssueCloneRequest,
    IssueCloneResponse,
    IssueFromTemplateRequest,
    IssueTemplateCreate,
    IssueTemplateResponse,
    IssueTemplateUpdate,
)
from personal_jira.services.template_service import TemplateService

router = APIRouter()


@router.post(
    "/templates",
    response_model=IssueTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    data: IssueTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> IssueTemplateResponse:
    service = TemplateService(db)
    template = await service.create_template(data)
    return IssueTemplateResponse.model_validate(template)


@router.get("/templates", response_model=list[IssueTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[IssueTemplateResponse]:
    service = TemplateService(db)
    templates = await service.list_templates(skip=skip, limit=limit)
    return [IssueTemplateResponse.model_validate(t) for t in templates]


@router.get("/templates/{template_id}", response_model=IssueTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> IssueTemplateResponse:
    service = TemplateService(db)
    template = await service.get_template(template_id)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )
    return IssueTemplateResponse.model_validate(template)


@router.patch("/templates/{template_id}", response_model=IssueTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    data: IssueTemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> IssueTemplateResponse:
    service = TemplateService(db)
    template = await service.update_template(template_id, data)
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )
    return IssueTemplateResponse.model_validate(template)


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = TemplateService(db)
    deleted = await service.delete_template(template_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )


@router.post(
    "/templates/create-issue",
    response_model=IssueTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_issue_from_template(
    req: IssueFromTemplateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TemplateService(db)
    try:
        issue = await service.create_issue_from_template(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    return issue


@router.post(
    "/issues/{issue_id}/clone",
    response_model=IssueCloneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clone_issue(
    issue_id: uuid.UUID,
    req: IssueCloneRequest,
    db: AsyncSession = Depends(get_db),
) -> IssueCloneResponse:
    service = TemplateService(db)
    try:
        cloned = await service.clone_issue(issue_id, req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    return IssueCloneResponse(
        id=cloned.id,
        source_issue_id=issue_id,
        title=cloned.title,
        description=cloned.description,
        status=cloned.status,
        priority=cloned.priority,
        issue_type=cloned.issue_type,
        created_at=cloned.created_at,
        updated_at=cloned.updated_at,
    )
