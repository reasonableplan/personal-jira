import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from personal_jira.models.base import Base


class ReviewDecision(str, enum.Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


REVIEW_TRANSITION_MAP: dict[ReviewDecision, str] = {
    ReviewDecision.APPROVED: "done",
    ReviewDecision.CHANGES_REQUESTED: "in_progress",
}


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    decision = Column(Enum(ReviewDecision), nullable=False)
    comment = Column(Text, nullable=True)
    reviewer = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    issue = relationship("Issue", back_populates="reviews")
