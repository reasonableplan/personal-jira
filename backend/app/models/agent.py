from datetime import datetime

from app.models.base import Base
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class AgentStatus:
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (
        Index("ix_agents_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AgentStatus.IDLE,
    )
    current_task_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        nullable=True,
    )
    last_heartbeat: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
