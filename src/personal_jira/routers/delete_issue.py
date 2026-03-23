from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_async_session
from personal_jira.models.issue import Issue

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: uuid.UUID,
    hard: bool = Query(default=False),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    issue = await db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )

    # Check for children — block deletion if any exist
    stmt = select(Issue).where(Issue.parent_id == issue_id).limit(1)
    result = await db.execute(stmt)
    child = result.scalar_one_or_none()
    if child is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Issue {issue_id} has children and cannot be deleted",
        )

    if hard:
        await db.delete(issue)
    else:
        issue.deleted_at = datetime.now(timezone.utc)

    await db.commit()
