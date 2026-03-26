from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.epic import Epic
    from app.models.task import Task


class Story(TimestampMixin, Base):
    __tablename__ = "stories"

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    epic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("epics.id", ondelete="CASCADE"),
    )
    position: Mapped[int] = mapped_column(default=0)

    epic: Mapped[Epic] = relationship(back_populates="stories")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="story",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
