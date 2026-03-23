import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.exceptions import (
    CircularDependencyError,
    DependencyNotFoundError,
    DuplicateDependencyError,
    IssueNotFoundError,
    SelfDependencyError,
)
from personal_jira.models.issue import Issue
from personal_jira.schemas.dependency import (
    DependencyCreate,
    DependencyListResponse,
    DependencyResponse,
)
from personal_jira.services.dependency_service import DependencyService

router = APIRouter(prefix="/api/v1/issues", tags=["dependencies"])


@router.post(
    "/{issue_id}/dependencies",
    response_model=DependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dependency(
    issue_id: uuid.UUID,
    body: DependencyCreate,
    db: Session = Depends(get_db),
) -> DependencyResponse:
    try:
        dep = DependencyService.create(
            db, blocked_issue_id=issue_id, blocker_issue_id=body.blocker_issue_id
        )
    except SelfDependencyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IssueNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateDependencyError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CircularDependencyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DependencyResponse.model_validate(dep)


@router.get(
    "/{issue_id}/dependencies",
    response_model=DependencyListResponse,
)
def get_dependencies(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DependencyListResponse:
    issue = db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")

    blockers = DependencyService.get_blockers(db, issue_id=issue_id)
    blocks = DependencyService.get_blocked_by(db, issue_id=issue_id)
    return DependencyListResponse(
        blockers=[DependencyResponse.model_validate(d) for d in blockers],
        blocks=[DependencyResponse.model_validate(d) for d in blocks],
    )


@router.delete(
    "/{issue_id}/dependencies/{dependency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dependency(
    issue_id: uuid.UUID,
    dependency_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    try:
        DependencyService.delete(db, dependency_id=dependency_id)
    except DependencyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
