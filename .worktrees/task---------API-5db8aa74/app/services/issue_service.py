from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Issue


async def create_issue(
    db: AsyncSession,
    *,
    title: str,
    description: str | None = None,
    priority: str = "medium",
) -> Issue:
    issue = Issue(title=title, description=description, priority=priority)
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


async def get_issue(db: AsyncSession, issue_id: int) -> Issue:
    issue = await db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


async def list_issues(
    db: AsyncSession,
    *,
    status: str | None = None,
    priority: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Issue], int]:
    query = select(Issue)
    count_query = select(func.count()).select_from(Issue)
    if status:
        query = query.where(Issue.status == status)
        count_query = count_query.where(Issue.status == status)
    if priority:
        query = query.where(Issue.priority == priority)
        count_query = count_query.where(Issue.priority == priority)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0


async def update_issue(
    db: AsyncSession,
    issue_id: int,
    *,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
) -> Issue:
    issue = await get_issue(db, issue_id)
    if title is not None:
        issue.title = title
    if description is not None:
        issue.description = description
    if priority is not None:
        issue.priority = priority
    await db.commit()
    await db.refresh(issue)
    return issue


async def delete_issue(db: AsyncSession, issue_id: int) -> None:
    issue = await get_issue(db, issue_id)
    await db.delete(issue)
    await db.commit()


async def update_issue_status(db: AsyncSession, issue_id: int, *, status: str) -> Issue:
    issue = await get_issue(db, issue_id)
    issue.status = status
    await db.commit()
    await db.refresh(issue)
    return issue
