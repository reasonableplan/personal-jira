from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base

if TYPE_CHECKING:
    from personal_jira.models.issue import Issue


class CommentType(enum.Enum):
    GENERAL = "general"
    REVIEW = "review"
    FEEDBACK = "feedback"


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index("ix_comments_issue_id", "issue_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    comment_type: Mapped[CommentType] = mapped_column(default=CommentType.GENERAL)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    issue: Mapped["Issue"] = relationship(back_populates="comments")
