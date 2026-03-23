from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base

if TYPE_CHECKING:
    from personal_jira.models.comment import Comment
    from personal_jira.models.issue_dependency import IssueDependency
    from personal_jira.models.issue_label import IssueLabel


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="issue",
        cascade="all, delete-orphan",
    )
    issue_labels: Mapped[List["IssueLabel"]] = relationship(
        back_populates="issue",
        cascade="all, delete-orphan",
    )
    dependencies_from: Mapped[List["IssueDependency"]] = relationship(
        back_populates="from_issue",
        foreign_keys="[IssueDependency.from_issue_id]",
        cascade="all, delete-orphan",
    )
    dependencies_to: Mapped[List["IssueDependency"]] = relationship(
        back_populates="to_issue",
        foreign_keys="[IssueDependency.to_issue_id]",
        cascade="all, delete-orphan",
    )
