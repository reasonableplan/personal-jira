from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.issue import (
    IssueCreate,
    IssueListResponse,
    IssuePriority,
    IssueResponse,
    IssueStatus,
    IssueUpdate,
)
from app.services.issue_service import (
    create_issue,
    delete_issue,
    get_issue,
    list_issues,
    update_issue,
)

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create(body: IssueCreate, db: AsyncSession = Depends(get_db)) -> IssueResponse:
    issue = await create_issue(
        db,
        title=body.title,
        description=body.description,
        priority=body.priority.value,
    )
    return IssueResponse.model_validate(issue)


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_by_id(issue_id: int, db: AsyncSession = Depends(get_db)) -> IssueResponse:
    issue = await get_issue(db, issue_id)
    return IssueResponse.model_validate(issue)


@router.get("", response_model=IssueListResponse)
async def list_all(
    status: IssueStatus | None = None,
    priority: IssuePriority | None = None,
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> IssueListResponse:
    items, total = await list_issues(
        db,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        offset=offset,
        limit=limit,
    )
    return IssueListResponse(
        items=[IssueResponse.model_validate(i) for i in items],
        total=total,
    )


@router.put("/{issue_id}", response_model=IssueResponse)
async def update(
    issue_id: int, body: IssueUpdate, db: AsyncSession = Depends(get_db)
) -> IssueResponse:
    fields = body.model_dump(exclude_unset=True)
    if "priority" in fields and fields["priority"] is not None:
        fields["priority"] = fields["priority"].value
    if "status" in fields and fields["status"] is not None:
        fields["status"] = fields["status"].value
    issue = await update_issue(db, issue_id, **fields)
    return IssueResponse.model_validate(issue)


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(issue_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    await delete_issue(db, issue_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
