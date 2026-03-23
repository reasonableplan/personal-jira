import enum
from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from personal_jira.database import Base
from personal_jira.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin


class WebhookEventType(str, enum.Enum):
    ISSUE_CREATED = "issue.created"
    ISSUE_UPDATED = "issue.updated"
    ISSUE_DELETED = "issue.deleted"
    ISSUE_TRANSITIONED = "issue.transitioned"
    COMMENT_ADDED = "comment.added"


class Webhook(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "webhooks"

    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    event_types: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded list
    secret: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
