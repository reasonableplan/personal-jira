import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.sprint import SprintCreate, SprintResponse, SprintUpdate
from personal_jira.services.sprint import SprintService

router = APIRouter(prefix="/api/v1/sprints", tags=["sprints"])
sprint_service = SprintService()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SprintResponse)
async def create_sprint(
    data: SprintCreate, db: AsyncSession = Depends(get_db)
) -> SprintResponse:
    sprint = await sprint_service.create(db, data)
    return SprintResponse.model_validate(sprint)


@router.get("", response_model=list[SprintResponse])
async def list_sprints(
    db: AsyncSession = Depends(get_db),
) -> list[SprintResponse]:
    sprints = await sprint_service.list_all(db)
    return [SprintResponse.model_validate(s) for s in sprints]


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SprintResponse:
    sprint = await sprint_service.get_by_id(db, sprint_id)
    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return SprintResponse.model_validate(sprint)


@router.patch("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: uuid.UUID,
    data: SprintUpdate,
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    sprint = await sprint_service.update(db, sprint_id, data)
    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return SprintResponse.model_validate(sprint)


@router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    deleted = await sprint_service.delete(db, sprint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sprint not found")
