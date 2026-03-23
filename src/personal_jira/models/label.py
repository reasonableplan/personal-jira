from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base

if TYPE_CHECKING:
    from personal_jira.models.issue_label import IssueLabel


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("name", name="uq_labels_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    issue_labels: Mapped[List["IssueLabel"]] = relationship(
        back_populates="label",
        cascade="all, delete-orphan",
    )
