import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_async_session
from personal_jira.models.activity import ActivityType
from personal_jira.models.issue import Issue
from personal_jira.schemas.activity import ActivityListResponse
from personal_jira.services.activity_service import ActivityService, DEFAULT_LIMIT

router = APIRouter(prefix="/api/v1/issues", tags=["activities"])


async def _verify_issue_exists(
    issue_id: uuid.UUID, session: AsyncSession
) -> None:
    result = await session.execute(select(Issue).where(Issue.id == issue_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Issue not found")


@router.get("/{issue_id}/activities", response_model=ActivityListResponse)
async def get_activities(
    issue_id: uuid.UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=200),
    activity_type: Optional[ActivityType] = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
) -> ActivityListResponse:
    await _verify_issue_exists(issue_id, session)

    service = ActivityService(session)
    items = await service.get_timeline(
        issue_id, offset=offset, limit=limit, activity_type=activity_type
    )
    total = await service.count(issue_id, activity_type=activity_type)

    return ActivityListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )
