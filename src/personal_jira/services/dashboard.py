from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.issue import Issue
from src.personal_jira.schemas.dashboard import (
    AssigneeCount,
    DashboardStats,
    PriorityCount,
    StatusCount,
)

DONE_STATUS = "Done"


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_stats(self) -> DashboardStats:
        status_rows = await self._count_by(Issue.status)
        priority_rows = await self._count_by(Issue.priority)
        assignee_rows = await self._count_by(Issue.assignee_id)

        by_status = [StatusCount(status=row[0], count=row[1]) for row in status_rows]
        by_priority = [PriorityCount(priority=row[0], count=row[1]) for row in priority_rows]
        by_assignee = [AssigneeCount(assignee_id=row[0], count=row[1]) for row in assignee_rows]

        total = sum(s.count for s in by_status)
        done_count = next((s.count for s in by_status if s.status == DONE_STATUS), 0)
        completion_rate = (done_count / total * 100) if total > 0 else 0.0

        return DashboardStats(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            by_assignee=by_assignee,
            done_count=done_count,
            completion_rate=round(completion_rate, 2),
        )

    async def _count_by(self, column: object) -> list[tuple]:
        stmt = select(column, func.count()).group_by(column)
        result = await self._db.execute(stmt)
        return result.all()
