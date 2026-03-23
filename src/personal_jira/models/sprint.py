from datetime import date
from typing import Optional

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from personal_jira.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Sprint(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sprints"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
