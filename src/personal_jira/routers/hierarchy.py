from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.schemas.hierarchy import (
    IssueAncestorResponse,
    IssueChildResponse,
    IssueSubtreeResponse,
)
from personal_jira.services.hierarchy import HierarchyService

router = APIRouter(prefix="/api/v1/issues", tags=["hierarchy"])


@router.get("/{issue_id}/children", response_model=list[IssueChildResponse])
def get_children(
    issue_id: int,
    db: Session = Depends(get_db),
) -> list[IssueChildResponse]:
    svc = HierarchyService(db)
    try:
        children = svc.get_children(issue_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )
    return [IssueChildResponse.model_validate(c) for c in children]


@router.get("/{issue_id}/subtree", response_model=IssueSubtreeResponse)
def get_subtree(
    issue_id: int,
    max_depth: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> IssueSubtreeResponse:
    svc = HierarchyService(db)
    try:
        tree = svc.get_subtree(issue_id, max_depth=max_depth)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )
    return IssueSubtreeResponse.model_validate(tree)


@router.get("/{issue_id}/ancestors", response_model=list[IssueAncestorResponse])
def get_ancestors(
    issue_id: int,
    db: Session = Depends(get_db),
) -> list[IssueAncestorResponse]:
    svc = HierarchyService(db)
    try:
        ancestors = svc.get_ancestors(issue_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )
    return [IssueAncestorResponse.model_validate(a) for a in ancestors]
