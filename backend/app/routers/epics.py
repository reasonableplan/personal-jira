from datetime import UTC, datetime
from uuid import UUID

from app.database import get_session
from app.models.issue import Epic
from app.schemas.epic import (
    EpicCreate,
    EpicDetailResponse,
    EpicResponse,
    EpicUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/epics", tags=["epics"])


async def _get_epic_or_404(
    epic_id: UUID, session: AsyncSession
) -> Epic:
    result = await session.execute(select(Epic).where(Epic.id == epic_id))
    epic = result.scalar_one_or_none()
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic


@router.post("/", status_code=201, response_model=EpicResponse)
async def create_epic(
    body: EpicCreate,
    session: AsyncSession = Depends(get_session),
) -> Epic:
    epic = Epic(title=body.title, description=body.description)
    session.add(epic)
    await session.commit()
    await session.refresh(epic)
    return epic


@router.get("/")
async def list_epics(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict:
    query = select(Epic)
    count_query = select(func.count()).select_from(Epic)

    if status is not None:
        query = query.where(Epic.status == status)
        count_query = count_query.where(Epic.status == status)

    total: int = (await session.execute(count_query)).scalar_one()

    query = query.order_by(Epic.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await session.execute(query)
    epics = result.scalars().all()

    return {
        "items": [EpicResponse.model_validate(e) for e in epics],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/{epic_id}", response_model=EpicDetailResponse)
async def get_epic(
    epic_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Epic:
    result = await session.execute(
        select(Epic).options(selectinload(Epic.stories)).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic


@router.patch("/{epic_id}", response_model=EpicResponse)
async def update_epic(
    epic_id: UUID,
    body: EpicUpdate,
    session: AsyncSession = Depends(get_session),
) -> Epic:
    epic = await _get_epic_or_404(epic_id, session)
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(epic, key, value)
    epic.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(epic)
    return epic


@router.delete("/{epic_id}", status_code=204)
async def delete_epic(
    epic_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    epic = await _get_epic_or_404(epic_id, session)
    await session.delete(epic)
    await session.commit()
