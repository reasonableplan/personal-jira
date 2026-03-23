import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from personal_jira.config import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT
from personal_jira.database import get_db
from personal_jira.models.issue import Issue, IssueStatus, IssuePriority
from personal_jira.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
)

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=201)
def create_issue(payload: IssueCreate, db: Session = Depends(get_db)) -> Issue:
    if payload.parent_id:
        parent = db.query(Issue).filter(
            Issue.id == payload.parent_id, Issue.deleted_at.is_(None)
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent issue not found")

    issue = Issue(**payload.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("", response_model=IssueListResponse)
def list_issues(
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT),
    status: str | None = None,
    priority: str | None = None,
    assignee: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(Issue).filter(Issue.deleted_at.is_(None))

    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee:
        query = query.filter(Issue.assignee == assignee)

    total = query.count()
    items = query.order_by(Issue.created_at.desc()).offset(offset).limit(limit).all()

    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: uuid.UUID, db: Session = Depends(get_db)) -> Issue:
    issue = db.query(Issue).filter(
        Issue.id == issue_id, Issue.deleted_at.is_(None)
    ).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: uuid.UUID, payload: IssueUpdate, db: Session = Depends(get_db)
) -> Issue:
    issue = db.query(Issue).filter(
        Issue.id == issue_id, Issue.deleted_at.is_(None)
    ).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/{issue_id}", status_code=204)
def delete_issue(
    issue_id: uuid.UUID,
    hard: bool = Query(False),
    db: Session = Depends(get_db),
) -> None:
    issue = db.query(Issue).filter(
        Issue.id == issue_id, Issue.deleted_at.is_(None)
    ).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    children = db.query(Issue).filter(
        Issue.parent_id == issue_id, Issue.deleted_at.is_(None)
    ).count()
    if children > 0:
        raise HTTPException(
            status_code=409, detail="Cannot delete issue with active children"
        )

    if hard:
        db.delete(issue)
    else:
        issue.deleted_at = datetime.now(timezone.utc)

    db.commit()
