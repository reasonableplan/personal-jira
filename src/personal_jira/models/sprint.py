import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base


class SprintStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SprintStatus] = mapped_column(
        Enum(SprintStatus, name="sprint_status", values_callable=lambda x: [e.value for e in x]),
        default=SprintStatus.PLANNING,
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    issues: Mapped[list["Issue"]] = relationship(
        "Issue", back_populates="sprint", lazy="selectin"
    )
