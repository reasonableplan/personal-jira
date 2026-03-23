import enum
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from personal_jira.models.agent import Agent


class ArtifactType(str, enum.Enum):
    CODE = "code"
    TEST = "test"
    CONFIG = "config"
    DOCS = "docs"


class CodeArtifact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "code_artifacts"

    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ArtifactType.CODE
    )
    files: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    pr_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    agent: Mapped["Agent"] = relationship(back_populates="code_artifacts")
