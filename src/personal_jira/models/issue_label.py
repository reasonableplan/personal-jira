from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base

if TYPE_CHECKING:
    from personal_jira.models.issue import Issue
    from personal_jira.models.label import Label


class IssueLabel(Base):
    __tablename__ = "issue_labels"
    __table_args__ = (
        UniqueConstraint("issue_id", "label_id", name="uq_issue_label"),
        Index("ix_issue_labels_issue_id", "issue_id"),
        Index("ix_issue_labels_label_id", "label_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    label_id: Mapped[int] = mapped_column(ForeignKey("labels.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    issue: Mapped["Issue"] = relationship(back_populates="issue_labels")
    label: Mapped["Label"] = relationship(back_populates="issue_labels")
