from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from personal_jira.database import Base
from personal_jira.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin


class IssueTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issue_templates"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    title_pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    labels: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON-encoded list
