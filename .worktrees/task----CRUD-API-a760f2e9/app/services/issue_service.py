from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import IssueNotFoundException
from app.models import Issue


async def create_issue(
    session: AsyncSession,
    *,
    title: str,
    description: str | None = None,
    priority: str = "medium",
) -> Issue:
    issue = Issue(title=title, description=description, priority=priority)
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return issue


async def get_issue(session: AsyncSession, issue_id: int) -> Issue:
    issue = await session.get(Issue, issue_id)
    if issue is None:
        raise IssueNotFoundException(issue_id)
    return issue


async def list_issues(
    session: AsyncSession,
    *,
    status: str | None = None,
    priority: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Issue], int]:
    query = select(Issue)
    count_query = select(func.count()).select_from(Issue)

    if status is not None:
        query = query.where(Issue.status == status)
        count_query = count_query.where(Issue.status == status)
    if priority is not None:
        query = query.where(Issue.priority == priority)
        count_query = count_query.where(Issue.priority == priority)

    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    items = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar_one()
    return items, total


async def update_issue(
    session: AsyncSession,
    issue_id: int,
    **fields: object,
) -> Issue:
    issue = await get_issue(session, issue_id)
    for key, value in fields.items():
        if value is not None:
            setattr(issue, key, value)
    await session.commit()
    await session.refresh(issue)
    return issue


async def delete_issue(session: AsyncSession, issue_id: int) -> None:
    issue = await get_issue(session, issue_id)
    await session.delete(issue)
    await session.commit()
