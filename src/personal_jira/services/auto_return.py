import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus

logger = logging.getLogger(__name__)

AUTO_RETURN_TIMEOUT_MINUTES: int = 30


class AutoReturnService:
    async def return_stale_issues(
        self,
        db: AsyncSession,
        timeout_minutes: int = AUTO_RETURN_TIMEOUT_MINUTES,
    ) -> list[Issue]:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)

        result = await db.execute(
            select(Issue).where(
                Issue.status == IssueStatus.IN_PROGRESS,
                Issue.assignee_id.isnot(None),
                Issue.started_at < cutoff,
            )
        )
        stale_issues: list[Issue] = list(result.scalars().all())

        if not stale_issues:
            return []

        returned_ids: list[uuid.UUID] = []
        for issue in stale_issues:
            issue.status = IssueStatus.READY
            issue.assignee_id = None
            issue.started_at = None
            returned_ids.append(issue.id)

        await db.commit()
        logger.info(
            "Auto-returned %d stale issues: %s",
            len(returned_ids),
            [str(uid) for uid in returned_ids],
        )
        return stale_issues
