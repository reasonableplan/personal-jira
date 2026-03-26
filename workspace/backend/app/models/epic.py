from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.story import Story


class EpicStatus(enum.StrEnum):
    PLANNING = "planning"
    ACTIVE = "active"
    DONE = "done"


class Epic(TimestampMixin, Base):
    __tablename__ = "epics"

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[EpicStatus] = mapped_column(default=EpicStatus.PLANNING)

    stories: Mapped[list[Story]] = relationship(
        back_populates="epic", cascade="all, delete-orphan"
    )
