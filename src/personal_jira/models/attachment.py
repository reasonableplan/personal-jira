import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.database import Base
from personal_jira.models.mixins import UUIDPrimaryKeyMixin
from personal_jira.models.mixins import TimestampMixin


class Attachment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "attachments"

    issue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    issue: Mapped["Issue"] = relationship(back_populates="attachments")
