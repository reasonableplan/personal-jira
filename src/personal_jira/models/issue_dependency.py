from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base

if TYPE_CHECKING:
    from personal_jira.models.issue import Issue


class DependencyType(enum.Enum):
    BLOCKED_BY = "blocked_by"
    BLOCKS = "blocks"


class IssueDependency(Base):
    __tablename__ = "issue_dependencies"
    __table_args__ = (
        UniqueConstraint("from_issue_id", "to_issue_id", name="uq_issue_dep_from_to"),
        Index("ix_issue_dep_from", "from_issue_id"),
        Index("ix_issue_dep_to", "to_issue_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    from_issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    to_issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    dependency_type: Mapped[DependencyType] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    from_issue: Mapped["Issue"] = relationship(
        back_populates="dependencies_from",
        foreign_keys=[from_issue_id],
    )
    to_issue: Mapped["Issue"] = relationship(
        back_populates="dependencies_to",
        foreign_keys=[to_issue_id],
    )
