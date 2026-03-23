import uuid
from typing import Optional

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.database import Base
from personal_jira.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin


class Issue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "issues"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="backlog")
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("issues.id"), nullable=True)
    labels: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    attachments: Mapped[list["Attachment"]] = relationship(back_populates="issue", cascade="all, delete-orphan")
