import enum
import uuid as _uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.database import Base


class IssueStatus(str, enum.Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[_uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), default=IssueStatus.BACKLOG, nullable=False
    )
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    blocked_by_deps: Mapped[list["IssueDependency"]] = relationship(
        "IssueDependency",
        foreign_keys="IssueDependency.blocked_issue_id",
        back_populates="blocked_issue",
        cascade="all, delete-orphan",
    )
    blocking_deps: Mapped[list["IssueDependency"]] = relationship(
        "IssueDependency",
        foreign_keys="IssueDependency.blocker_issue_id",
        back_populates="blocker_issue",
        cascade="all, delete-orphan",
    )


from personal_jira.models.dependency import IssueDependency  # noqa: E402
