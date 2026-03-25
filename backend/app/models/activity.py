import uuid
from datetime import datetime

from app.models.base import Base
from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column


class ActionType:
    STATUS_CHANGE = "status_change"
    COMMENT = "comment"
    REVIEW_FEEDBACK = "review_feedback"
    CODE_CHANGE = "code_change"


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (
        Index("ix_activities_task_id_created_at", "task_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )
    content: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
