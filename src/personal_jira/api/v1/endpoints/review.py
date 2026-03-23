import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from personal_jira.database import get_db
from personal_jira.exceptions import IssueNotFoundError, IssueNotInReviewError
from personal_jira.models.issue import IssueStatus
from personal_jira.models.review import REVIEW_TRANSITION_MAP
from personal_jira.schemas.review import ReviewCreate, ReviewResponse
from personal_jira.services.review_service import review_service

router = APIRouter(prefix="/api/v1/issues", tags=["reviews"])


@router.post(
    "/{issue_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_review(
    issue_id: uuid.UUID,
    data: ReviewCreate,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    try:
        review = review_service.submit_review(db, issue_id, data)
    except IssueNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except IssueNotInReviewError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    resulting_status = IssueStatus(REVIEW_TRANSITION_MAP[review.decision])
    return ReviewResponse(
        id=review.id,
        issue_id=review.issue_id,
        decision=review.decision,
        comment=review.comment,
        reviewer=review.reviewer,
        created_at=review.created_at,
        resulting_status=resulting_status,
    )


@router.get(
    "/{issue_id}/reviews",
    response_model=list[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
def get_reviews(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ReviewResponse]:
    reviews = review_service.get_reviews(db, issue_id)
    return [
        ReviewResponse(
            id=r.id,
            issue_id=r.issue_id,
            decision=r.decision,
            comment=r.comment,
            reviewer=r.reviewer,
            created_at=r.created_at,
            resulting_status=IssueStatus(REVIEW_TRANSITION_MAP[r.decision]),
        )
        for r in reviews
    ]
