import uuid
from typing import Sequence

from sqlalchemy.orm import Session

from personal_jira.exceptions import IssueNotFoundError, IssueNotInReviewError
from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.models.review import Review, ReviewDecision, REVIEW_TRANSITION_MAP
from personal_jira.schemas.review import ReviewCreate


class ReviewService:
    def _get_issue(self, db: Session, issue_id: uuid.UUID) -> Issue | None:
        return db.query(Issue).filter(Issue.id == issue_id).first()

    def submit_review(
        self, db: Session, issue_id: uuid.UUID, data: ReviewCreate
    ) -> Review:
        issue = self._get_issue(db, issue_id)
        if issue is None:
            raise IssueNotFoundError(issue_id)

        if issue.status != IssueStatus.IN_REVIEW:
            raise IssueNotInReviewError(issue_id, issue.status)

        target_status = REVIEW_TRANSITION_MAP[data.decision]
        issue.status = IssueStatus(target_status)

        review = Review(
            issue_id=issue_id,
            decision=data.decision,
            comment=data.comment,
            reviewer=data.reviewer,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    def get_reviews(
        self, db: Session, issue_id: uuid.UUID
    ) -> Sequence[Review]:
        return (
            db.query(Review)
            .filter(Review.issue_id == issue_id)
            .order_by(Review.created_at)
            .all()
        )


review_service = ReviewService()
