import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from personal_jira.models.base import Base


class IssueTemplate(Base):
    __tablename__ = "issue_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    default_title = Column(String(500), nullable=True)
    default_description = Column(Text, nullable=True)
    default_priority = Column(String(50), nullable=True)
    default_issue_type = Column(String(50), nullable=True)
    default_labels = Column(ARRAY(String), nullable=False, server_default="{}")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
