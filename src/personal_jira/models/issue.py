from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from personal_jira.models.issue_priority import IssuePriority
from personal_jira.models.issue_status import IssueStatus
from personal_jira.models.issue_type import IssueType


class Issue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issues"
    __table_args__ = (
        Index("ix_issues_status", "status"),
        Index("ix_issues_assignee", "assignee"),
        Index("ix_issues_priority", "priority"),
        Index("ix_issues_parent_id", "parent_id"),
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issue_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=IssueStatus.BACKLOG.value,
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=IssuePriority.MEDIUM.value,
    )
    assignee: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("issues.id"), nullable=True,
    )
    labels: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    required_skills: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    context_bundle: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    children: Mapped[list[Issue]] = relationship(
        "Issue", back_populates="parent", cascade="all, delete-orphan",
    )
    parent: Mapped[Optional[Issue]] = relationship(
        "Issue", back_populates="children", remote_side="Issue.id",
    )
