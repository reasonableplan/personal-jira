import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.assignee import AssigneeCreate, AssigneeResponse
from personal_jira.services.assignee_service import AssigneeService

router = APIRouter()


@router.post(
    "/issues/{issue_id}/assignees",
    response_model=AssigneeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_user(
    issue_id: uuid.UUID, data: AssigneeCreate, db: AsyncSession = Depends(get_db)
) -> AssigneeResponse:
    service = AssigneeService(db)
    assignee = await service.assign_user(issue_id, data)
    return AssigneeResponse.model_validate(assignee)


@router.get("/issues/{issue_id}/assignees", response_model=list[AssigneeResponse])
async def list_assignees(
    issue_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Sequence[AssigneeResponse]:
    service = AssigneeService(db)
    assignees = await service.list_assignees(issue_id)
    return [AssigneeResponse.model_validate(a) for a in assignees]


@router.delete(
    "/issues/{issue_id}/assignees/{assignee_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_assignee(
    issue_id: uuid.UUID, assignee_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    service = AssigneeService(db)
    await service.remove_assignee(issue_id, assignee_id)
