from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.models.comment import Comment
from personal_jira.models.issue import Issue
from personal_jira.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

router = APIRouter(
    prefix="/api/v1/issues/{issue_id}/comments",
    tags=["comments"],
)


def _get_issue_or_404(issue_id: uuid.UUID, db: Session) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None or getattr(issue, "deleted_at", None) is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )
    return issue


def _get_comment_or_404(
    issue_id: uuid.UUID, comment_id: uuid.UUID, db: Session
) -> Comment:
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.issue_id == issue_id)
        .first()
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment {comment_id} not found",
        )
    return comment


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: uuid.UUID,
    body: CommentCreate,
    db: Session = Depends(get_db),
) -> Comment:
    _get_issue_or_404(issue_id, db)
    comment = Comment(
        issue_id=issue_id,
        author=body.author,
        content=body.content,
        comment_type=body.comment_type,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=List[CommentResponse])
def list_comments(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> list[Comment]:
    _get_issue_or_404(issue_id, db)
    return (
        db.query(Comment)
        .filter(Comment.issue_id == issue_id)
        .order_by(Comment.created_at)
        .offset(offset)
        .limit(min(limit, MAX_LIMIT))
        .all()
    )


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Comment:
    _get_issue_or_404(issue_id, db)
    return _get_comment_or_404(issue_id, comment_id, db)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    body: CommentUpdate,
    db: Session = Depends(get_db),
) -> Comment:
    _get_issue_or_404(issue_id, db)
    comment = _get_comment_or_404(issue_id, comment_id, db)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    issue_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    _get_issue_or_404(issue_id, db)
    comment = _get_comment_or_404(issue_id, comment_id, db)
    db.delete(comment)
    db.commit()
