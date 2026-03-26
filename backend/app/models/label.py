from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.task_label import task_labels

if TYPE_CHECKING:
    from app.models.task import Task


class Label(TimestampMixin, Base):
    __tablename__ = "labels"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str] = mapped_column(String(7))

    tasks: Mapped[list[Task]] = relationship(secondary=task_labels, back_populates="labels")
