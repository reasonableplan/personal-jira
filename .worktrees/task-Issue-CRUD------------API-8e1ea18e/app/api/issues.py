from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import IssueNotFoundException
from app.models.issue import Issue
from app.schemas.issue import (
    IssueCreate,
    IssueListResponse,
    IssueResponse,
    IssueStatus,
    IssueUpdate,
    StatusUpdate,
)

router = APIRouter(prefix="/issues", tags=["issues"])


async def _get_issue_or_404(issue_id: int, db: AsyncSession) -> Issue:
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if issue is None:
        raise IssueNotFoundException(issue_id)
    return issue


@router.post("/", response_model=IssueResponse, status_code=201)
async def create_issue(body: IssueCreate, db: AsyncSession = Depends(get_db)) -> Issue:
    issue = Issue(**body.model_dump())
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: int, db: AsyncSession = Depends(get_db)) -> Issue:
    return await _get_issue_or_404(issue_id, db)


@router.get("/", response_model=IssueListResponse)
async def list_issues(
    status: IssueStatus | None = None,
    priority: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    query = select(Issue)
    count_query = select(func.count()).select_from(Issue)

    if status is not None:
        query = query.where(Issue.status == status.value)
        count_query = count_query.where(Issue.status == status.value)
    if priority is not None:
        query = query.where(Issue.priority == priority)
        count_query = count_query.where(Issue.priority == priority)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query)
    items = list(result.scalars().all())

    return {"items": items, "total": total}


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int, body: IssueUpdate, db: AsyncSession = Depends(get_db)
) -> Issue:
    issue = await _get_issue_or_404(issue_id, db)
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    issue.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(issue)
    return issue


@router.delete("/{issue_id}", status_code=204)
async def delete_issue(
    issue_id: int, db: AsyncSession = Depends(get_db)
) -> Response:
    issue = await _get_issue_or_404(issue_id, db)
    await db.delete(issue)
    await db.commit()
    return Response(status_code=204)


@router.patch("/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(
    issue_id: int, body: StatusUpdate, db: AsyncSession = Depends(get_db)
) -> Issue:
    issue = await _get_issue_or_404(issue_id, db)
    issue.status = body.status.value
    issue.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(issue)
    return issue
