import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue
from personal_jira.models.label import Label
from personal_jira.schemas.label import LabelCreate


class LabelService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_issue_or_404(self, issue_id: uuid.UUID) -> Issue:
        result = await self.db.execute(select(Issue).where(Issue.id == issue_id))
        issue = result.scalar_one_or_none()
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue

    async def add_label(self, issue_id: uuid.UUID, data: LabelCreate) -> Label:
        await self._get_issue_or_404(issue_id)
        label = Label(issue_id=issue_id, name=data.name)
        self.db.add(label)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Label already exists")
        await self.db.refresh(label)
        return label

    async def list_labels(self, issue_id: uuid.UUID) -> Sequence[Label]:
        await self._get_issue_or_404(issue_id)
        result = await self.db.execute(select(Label).where(Label.issue_id == issue_id))
        return result.scalars().all()

    async def delete_label(self, issue_id: uuid.UUID, label_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Label).where(Label.id == label_id, Label.issue_id == issue_id)
        )
        label = result.scalar_one_or_none()
        if not label:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
        await self.db.delete(label)
        await self.db.commit()
