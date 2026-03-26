from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.task import Task


class StoryStatus(enum.StrEnum):
    BACKLOG = "backlog"
    ACTIVE = "active"
    DONE = "done"


class Story(TimestampMixin, Base):
    __tablename__ = "stories"
    __table_args__ = (
        Index("ix_stories_epic_id", "epic_id"),
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[StoryStatus] = mapped_column(default=StoryStatus.BACKLOG)
    epic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("epics.id", ondelete="CASCADE"),
    )

    epic: Mapped[Epic] = relationship(back_populates="stories")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )
