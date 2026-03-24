from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

STATUS_VALUES = ("todo", "in_progress", "done")
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
DEFAULT_STATUS = "todo"


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        CheckConstraint(f"status IN {STATUS_VALUES}", name="ck_issues_status"),
        CheckConstraint(
            f"priority >= {MIN_PRIORITY} AND priority <= {MAX_PRIORITY}",
            name="ck_issues_priority",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default=DEFAULT_STATUS, index=True, nullable=False
    )
    priority: Mapped[int] = mapped_column(
        Integer, default=DEFAULT_PRIORITY, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now())
