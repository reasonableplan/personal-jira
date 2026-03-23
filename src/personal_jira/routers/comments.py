from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_async_session
from personal_jira.models.comment import Comment, CommentType
from personal_jira.models.issue import Issue

router = APIRouter(
    prefix="/api/v1/issues/{issue_id}/comments",
    tags=["comments"],
)


class CommentCreate(BaseModel):
    body: str
    author: str
    comment_type: CommentType = CommentType.GENERAL


class CommentUpdate(BaseModel):
    body: str | None = None
    comment_type: CommentType | None = None


class CommentResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    body: str
    author: str
    comment_type: str
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj: Comment) -> "CommentResponse":
        return cls(
            id=obj.id,
            issue_id=obj.issue_id,
            body=obj.body,
            author=obj.author,
            comment_type=obj.comment_type.value if hasattr(obj.comment_type, "value") else obj.comment_type,
            created_at=obj.created_at.isoformat(),
        )


async def _get_issue_or_404(issue_id: uuid.UUID, db: AsyncSession) -> Issue:
    issue = await db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")
    return issue


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_comment(
    issue_id: uuid.UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    await _get_issue_or_404(issue_id, db)
    comment = Comment(
        issue_id=issue_id,
        body=payload.body,
        author=payload.author,
        comment_type=payload.comment_type,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return CommentResponse.from_orm(comment).model_dump()


@router.get("")
async def list_comments(
    issue_id: uuid.UUID,
    comment_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_async_session),
) -> list[dict]:
    await _get_issue_or_404(issue_id, db)
    stmt = select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.created_at)
    if comment_type is not None:
        stmt = stmt.where(Comment.comment_type == comment_type)
    result = await db.execute(stmt)
    comments = result.scalars().all()
    return [CommentResponse.from_orm(c).model_dump() for c in comments]


@router.patch("/{comment_id}")
async def update_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    payload: CommentUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    await _get_issue_or_404(issue_id, db)
    comment = await db.get(Comment, comment_id)
    if comment is None or comment.issue_id != issue_id:
        raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")
    if payload.body is not None:
        comment.body = payload.body
    if payload.comment_type is not None:
        comment.comment_type = payload.comment_type
    await db.commit()
    await db.refresh(comment)
    return CommentResponse.from_orm(comment).model_dump()


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await _get_issue_or_404(issue_id, db)
    comment = await db.get(Comment, comment_id)
    if comment is None or comment.issue_id != issue_id:
        raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")
    await db.delete(comment)
    await db.commit()
