import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.core.database import get_db
from personal_jira.schemas.label import LabelCreate, LabelResponse
from personal_jira.services.label_service import LabelService

router = APIRouter()


@router.post(
    "/issues/{issue_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_label(
    issue_id: uuid.UUID, data: LabelCreate, db: AsyncSession = Depends(get_db)
) -> LabelResponse:
    service = LabelService(db)
    label = await service.add_label(issue_id, data)
    return LabelResponse.model_validate(label)


@router.get("/issues/{issue_id}/labels", response_model=list[LabelResponse])
async def list_labels(
    issue_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Sequence[LabelResponse]:
    service = LabelService(db)
    labels = await service.list_labels(issue_id)
    return [LabelResponse.model_validate(l) for l in labels]


@router.delete(
    "/issues/{issue_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_label(
    issue_id: uuid.UUID, label_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    service = LabelService(db)
    await service.delete_label(issue_id, label_id)
