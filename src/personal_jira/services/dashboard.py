from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.schemas.dashboard import DashboardResponse

ALL_STATUSES = [s.value for s in IssueStatus]
ALL_PRIORITIES = ["critical", "high", "medium", "low"]


async def get_dashboard(db: AsyncSession) -> DashboardResponse:
    result = await db.execute(select(Issue))
    issues = result.scalars().all()

    status_counts = Counter(i.status.value if isinstance(i.status, IssueStatus) else i.status for i in issues)
    priority_counts = Counter(i.priority for i in issues)

    by_status = {s: status_counts.get(s, 0) for s in ALL_STATUSES}
    by_priority = {p: priority_counts.get(p, 0) for p in ALL_PRIORITIES}

    return DashboardResponse(
        total=len(issues),
        by_status=by_status,
        by_priority=by_priority,
    )
