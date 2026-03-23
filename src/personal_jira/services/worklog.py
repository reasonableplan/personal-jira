import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue
from personal_jira.models.worklog import WorkLog
from personal_jira.schemas.worklog import WorkLogCreate


class WorkLogService:
    async def _get_issue_or_raise(self, db: AsyncSession, issue_id: uuid.UUID) -> Issue:
        result = await db.execute(select(Issue).where(Issue.id == issue_id))
        issue = result.scalar_one_or_none()
        if issue is None or issue.deleted_at is not None:
            raise ValueError("Issue not found")
        return issue

    async def create(
        self, db: AsyncSession, issue_id: uuid.UUID, data: WorkLogCreate
    ) -> WorkLog:
        await self._get_issue_or_raise(db, issue_id)
        worklog = WorkLog(
            issue_id=issue_id,
            agent_id=data.agent_id,
            llm_calls=data.llm_calls,
            tokens_used=data.tokens_used,
            content=data.content,
        )
        db.add(worklog)
        await db.commit()
        await db.refresh(worklog)
        return worklog

    async def list_by_issue(
        self, db: AsyncSession, issue_id: uuid.UUID
    ) -> Sequence[WorkLog]:
        await self._get_issue_or_raise(db, issue_id)
        result = await db.execute(
            select(WorkLog)
            .where(WorkLog.issue_id == issue_id)
            .order_by(WorkLog.created_at.desc())
        )
        return result.scalars().all()
