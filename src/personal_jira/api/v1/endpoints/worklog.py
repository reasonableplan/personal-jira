import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.worklog import WorkLogCreate, WorkLogResponse
from personal_jira.services.worklog import WorkLogService

router = APIRouter(prefix="/api/v1/issues", tags=["worklogs"])


@router.post(
    "/{issue_id}/worklogs",
    response_model=WorkLogResponse,
    status_code=201,
)
async def create_worklog(
    issue_id: uuid.UUID,
    data: WorkLogCreate,
    db: AsyncSession = Depends(get_db),
) -> WorkLogResponse:
    service = WorkLogService()
    try:
        worklog = await service.create(db, issue_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return worklog


@router.get(
    "/{issue_id}/worklogs",
    response_model=List[WorkLogResponse],
)
async def list_worklogs(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[WorkLogResponse]:
    service = WorkLogService()
    try:
        worklogs = await service.list_by_issue(db, issue_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return worklogs
