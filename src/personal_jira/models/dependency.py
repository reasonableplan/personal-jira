import uuid as _uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.database import Base


class IssueDependency(Base):
    __tablename__ = "issue_dependencies"
    __table_args__ = (
        UniqueConstraint("blocked_issue_id", "blocker_issue_id", name="uq_dependency"),
        CheckConstraint(
            "blocked_issue_id != blocker_issue_id", name="ck_no_self_dependency"
        ),
    )

    id: Mapped[_uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    blocked_issue_id: Mapped[_uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
    )
    blocker_issue_id: Mapped[_uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    blocked_issue: Mapped["Issue"] = relationship(
        "Issue",
        foreign_keys=[blocked_issue_id],
        back_populates="blocked_by_deps",
    )
    blocker_issue: Mapped["Issue"] = relationship(
        "Issue",
        foreign_keys=[blocker_issue_id],
        back_populates="blocking_deps",
    )


from personal_jira.models.issue import Issue  # noqa: E402, F811
