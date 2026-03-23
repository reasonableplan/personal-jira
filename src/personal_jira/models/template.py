import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from personal_jira.models.base import Base


class IssueTemplate(Base):
    __tablename__ = "issue_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title_pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    description_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_issue_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_labels: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
