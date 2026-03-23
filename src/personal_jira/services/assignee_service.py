import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.assignee import Assignee
from personal_jira.models.issue import Issue
from personal_jira.schemas.assignee import AssigneeCreate


class AssigneeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_issue_or_404(self, issue_id: uuid.UUID) -> Issue:
        result = await self.db.execute(select(Issue).where(Issue.id == issue_id))
        issue = result.scalar_one_or_none()
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue

    async def assign_user(self, issue_id: uuid.UUID, data: AssigneeCreate) -> Assignee:
        await self._get_issue_or_404(issue_id)
        assignee = Assignee(issue_id=issue_id, user_id=data.user_id)
        self.db.add(assignee)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already assigned")
        await self.db.refresh(assignee)
        return assignee

    async def list_assignees(self, issue_id: uuid.UUID) -> Sequence[Assignee]:
        await self._get_issue_or_404(issue_id)
        result = await self.db.execute(select(Assignee).where(Assignee.issue_id == issue_id))
        return result.scalars().all()

    async def remove_assignee(self, issue_id: uuid.UUID, assignee_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Assignee).where(Assignee.id == assignee_id, Assignee.issue_id == issue_id)
        )
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
        await self.db.delete(assignee)
        await self.db.commit()
