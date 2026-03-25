from app.database import get_db as get_session
from app.models import Task
from app.schemas.label import (
    LabelCreate,
    LabelResponse,
    LabelUpdate,
    TaskLabelsAttach,
)
from app.services.label import label_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

HTTP_404_LABEL = "Label not found"
HTTP_404_TASK = "Task not found"
HTTP_409_DUPLICATE = "Label name already exists"

router = APIRouter(tags=["labels"])


@router.post(
    "/api/labels", response_model=LabelResponse, status_code=status.HTTP_201_CREATED
)
async def create_label(
    body: LabelCreate, session: AsyncSession = Depends(get_session)
) -> LabelResponse:
    existing = await label_service.get_by_name(session, body.name)
    if existing:
        raise HTTPException(status_code=409, detail=HTTP_409_DUPLICATE)
    label = await label_service.create(session, body)
    return LabelResponse.model_validate(label, from_attributes=True)


@router.get("/api/labels", response_model=list[LabelResponse])
async def list_labels(
    session: AsyncSession = Depends(get_session),
) -> list[LabelResponse]:
    labels = await label_service.list_all(session)
    return [
        LabelResponse.model_validate(label, from_attributes=True)
        for label in labels
    ]


@router.patch("/api/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: str,
    body: LabelUpdate,
    session: AsyncSession = Depends(get_session),
) -> LabelResponse:
    if body.name is not None:
        existing = await label_service.get_by_name(session, body.name)
        if existing and existing.id != label_id:
            raise HTTPException(status_code=409, detail=HTTP_409_DUPLICATE)
    label = await label_service.update(session, label_id, body)
    if not label:
        raise HTTPException(status_code=404, detail=HTTP_404_LABEL)
    return LabelResponse.model_validate(label, from_attributes=True)


@router.delete(
    "/api/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_label(
    label_id: str, session: AsyncSession = Depends(get_session)
) -> None:
    deleted = await label_service.delete(session, label_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=HTTP_404_LABEL)


@router.post("/api/tasks/{task_id}/labels", response_model=list[str])
async def attach_labels_to_task(
    task_id: str,
    body: TaskLabelsAttach,
    session: AsyncSession = Depends(get_session),
) -> list[str]:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=HTTP_404_TASK)
    return await label_service.attach_labels_to_task(
        session, task_id, body.label_ids
    )


@router.delete(
    "/api/tasks/{task_id}/labels/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def detach_label_from_task(
    task_id: str,
    label_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    detached = await label_service.detach_label_from_task(
        session, task_id, label_id
    )
    if not detached:
        raise HTTPException(status_code=404, detail=HTTP_404_LABEL)
