import enum
import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.personal_jira.database import Base


class WebhookType(str, enum.Enum):
    DISCORD = "discord"
    SLACK = "slack"


class WebhookEvent(str, enum.Enum):
    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    ISSUE_DELETED = "issue_deleted"
    ISSUE_TRANSITIONED = "issue_transitioned"
    ISSUE_COMMENT_ADDED = "issue_comment_added"


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[uuid_pkg.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    webhook_type: Mapped[WebhookType] = mapped_column(
        Enum(WebhookType), nullable=False
    )
    events: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
