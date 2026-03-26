from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.task_label import task_labels

if TYPE_CHECKING:
    from app.models.label import Label
    from app.models.story import Story


class TaskStatus(enum.StrEnum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    DONE = "done"


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_tasks_priority"),
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.BACKLOG)
    priority: Mapped[int] = mapped_column(default=3)
    story_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"),
    )
    position: Mapped[int] = mapped_column(default=0)

    story: Mapped[Story] = relationship(back_populates="tasks")
    labels: Mapped[list[Label]] = relationship(secondary=task_labels, back_populates="tasks")
