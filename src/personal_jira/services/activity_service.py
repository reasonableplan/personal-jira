import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.activity import ActivityLog, ActivityType

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


class ActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        issue_id: uuid.UUID,
        activity_type: ActivityType,
        actor: str = "system",
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> ActivityLog:
        log = ActivityLog(
            id=uuid.uuid4(),
            issue_id=issue_id,
            activity_type=activity_type,
            actor=actor,
            old_value=old_value,
            new_value=new_value,
            detail=detail,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def get_timeline(
        self,
        issue_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
        activity_type: Optional[ActivityType] = None,
    ) -> list[ActivityLog]:
        limit = min(limit, MAX_LIMIT)
        stmt = (
            select(ActivityLog)
            .where(ActivityLog.issue_id == issue_id)
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if activity_type is not None:
            stmt = stmt.where(ActivityLog.activity_type == activity_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        issue_id: uuid.UUID,
        *,
        activity_type: Optional[ActivityType] = None,
    ) -> int:
        stmt = select(func.count()).select_from(ActivityLog).where(
            ActivityLog.issue_id == issue_id
        )
        if activity_type is not None:
            stmt = stmt.where(ActivityLog.activity_type == activity_type)
        result = await self._session.execute(stmt)
        return result.scalar_one()
