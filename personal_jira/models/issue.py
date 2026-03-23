import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, Index, Enum, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.database import Base


class IssueType(str, enum.Enum):
    EPIC = "Epic"
    STORY = "Story"
    TASK = "Task"
    SUBTASK = "SubTask"


class IssueStatus(str, enum.Enum):
    BACKLOG = "Backlog"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    BLOCKED = "Blocked"
    DONE = "Done"
    CANCELLED = "Cancelled"


class IssuePriority(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    TRIVIAL = "Trivial"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    issue_type: Mapped[IssueType] = mapped_column(
        Enum(IssueType, name="issue_type_enum"), nullable=False
    )
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, name="issue_status_enum"),
        nullable=False,
        default=IssueStatus.BACKLOG,
    )
    priority: Mapped[IssuePriority] = mapped_column(
        Enum(IssuePriority, name="issue_priority_enum"),
        nullable=False,
        default=IssuePriority.MEDIUM,
    )
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True
    )
    labels: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True, default=list)
    context_bundle: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    children: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["Issue | None"] = relationship(
        "Issue", back_populates="children", remote_side=[id]
    )

    __table_args__ = (
        Index("ix_issues_status", "status"),
        Index("ix_issues_assignee", "assignee"),
        Index("ix_issues_priority", "priority"),
        Index("ix_issues_parent_id", "parent_id"),
    )
