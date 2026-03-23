from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.models.sprint import SprintStatus
from personal_jira.schemas.sprint import (
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintListResponse,
    SprintIssueAdd,
)
from personal_jira.schemas.issue import IssueResponse
from personal_jira.services.sprint_service import SprintService

router = APIRouter(prefix="/api/v1/sprints", tags=["sprints"])


def _get_service(db: AsyncSession = Depends(get_db)) -> SprintService:
    return SprintService(db)


@router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    data: SprintCreate,
    service: SprintService = Depends(_get_service),
) -> SprintResponse:
    sprint = await service.create(data)
    return SprintResponse.model_validate(sprint)


@router.get("", response_model=SprintListResponse)
async def list_sprints(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SprintStatus] = Query(None, alias="status"),
    service: SprintService = Depends(_get_service),
) -> SprintListResponse:
    sprints, total = await service.list_sprints(
        offset=offset, limit=limit, status=status_filter
    )
    return SprintListResponse(
        items=[SprintResponse.model_validate(s) for s in sprints],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: UUID,
    service: SprintService = Depends(_get_service),
) -> SprintResponse:
    sprint = await service.get_by_id(sprint_id)
    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return SprintResponse.model_validate(sprint)


@router.patch("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: UUID,
    data: SprintUpdate,
    service: SprintService = Depends(_get_service),
) -> SprintResponse:
    sprint = await service.update(sprint_id, data)
    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return SprintResponse.model_validate(sprint)


@router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: UUID,
    service: SprintService = Depends(_get_service),
) -> None:
    deleted = await service.delete(sprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sprint not found")


@router.post("/{sprint_id}/issues", response_model=IssueResponse)
async def add_issue_to_sprint(
    sprint_id: UUID,
    data: SprintIssueAdd,
    service: SprintService = Depends(_get_service),
) -> IssueResponse:
    result = await service.add_issue(sprint_id, data.issue_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    if result is False:
        raise HTTPException(status_code=404, detail="Issue not found")

    db = service._db
    from personal_jira.models.issue import Issue
    from sqlalchemy import select

    issue_result = await db.execute(
        select(Issue).where(Issue.id == data.issue_id)
    )
    issue = issue_result.scalar_one()
    return IssueResponse.model_validate(issue)


@router.delete(
    "/{sprint_id}/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_issue_from_sprint(
    sprint_id: UUID,
    issue_id: UUID,
    service: SprintService = Depends(_get_service),
) -> None:
    removed = await service.remove_issue(sprint_id, issue_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Issue not found in sprint")


@router.get("/{sprint_id}/issues", response_model=list[IssueResponse])
async def get_sprint_issues(
    sprint_id: UUID,
    service: SprintService = Depends(_get_service),
) -> list[IssueResponse]:
    issues = await service.get_sprint_issues(sprint_id)
    if issues is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return [IssueResponse.model_validate(i) for i in issues]
