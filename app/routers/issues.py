from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.issue import IssueStatus, IssuePriority, IssueType
from app.schemas.issue_search import IssueSearchParams
from app.services.issue_search_service import IssueSearchService

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])

issue_search_service = IssueSearchService()


@router.get("")
def list_issues(
    status: Optional[list[IssueStatus]] = Query(None),
    priority: Optional[list[IssuePriority]] = Query(None),
    assignee: Optional[str] = Query(None),
    label: Optional[list[str]] = Query(None),
    issue_type: Optional[IssueType] = Query(None),
    q: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db),
):
    params = IssueSearchParams(
        status=status,
        priority=priority,
        assignee=assignee,
        label=label,
        issue_type=issue_type,
        q=q,
        sort_by=sort_by,
        sort_order=sort_order,
        offset=offset,
        limit=limit,
    )
    result = issue_search_service.search(db, params)
    return {
        "items": [
            {
                "id": str(issue.id),
                "title": issue.title,
                "description": issue.description,
                "status": issue.status.value if issue.status else None,
                "priority": issue.priority.value if issue.priority else None,
                "issue_type": issue.issue_type.value if issue.issue_type else None,
                "assignee": issue.assignee,
                "labels": issue.labels or [],
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            }
            for issue in result.items
        ],
        "total": result.total,
        "offset": result.offset,
        "limit": result.limit,
    }
