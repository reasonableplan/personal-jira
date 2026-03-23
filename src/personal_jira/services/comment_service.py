import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.comment import Comment
from personal_jira.models.issue import Issue
from personal_jira.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_issue_or_404(self, issue_id: uuid.UUID) -> Issue:
        result = await self.db.execute(select(Issue).where(Issue.id == issue_id))
        issue = result.scalar_one_or_none()
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue

    async def _get_comment_or_404(self, issue_id: uuid.UUID, comment_id: uuid.UUID) -> Comment:
        result = await self.db.execute(
            select(Comment).where(Comment.id == comment_id, Comment.issue_id == issue_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        return comment

    async def create_comment(self, issue_id: uuid.UUID, data: CommentCreate) -> Comment:
        await self._get_issue_or_404(issue_id)
        comment = Comment(issue_id=issue_id, content=data.content, author=data.author)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def list_comments(self, issue_id: uuid.UUID) -> Sequence[Comment]:
        await self._get_issue_or_404(issue_id)
        result = await self.db.execute(
            select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.created_at)
        )
        return result.scalars().all()

    async def update_comment(
        self, issue_id: uuid.UUID, comment_id: uuid.UUID, data: CommentUpdate
    ) -> Comment:
        comment = await self._get_comment_or_404(issue_id, comment_id)
        comment.content = data.content
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete_comment(self, issue_id: uuid.UUID, comment_id: uuid.UUID) -> None:
        comment = await self._get_comment_or_404(issue_id, comment_id)
        await self.db.delete(comment)
        await self.db.commit()
