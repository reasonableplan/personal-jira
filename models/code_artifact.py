import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from database import Base


class ArtifactType(str, enum.Enum):
    FILE = "file"
    COMMIT = "commit"
    PULL_REQUEST = "pull_request"


class CodeArtifact(Base):
    __tablename__ = "code_artifacts"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artifact_type: ArtifactType = Column(
        Enum(ArtifactType, name="artifact_type", create_constraint=True),
        nullable=False,
    )
    identifier: str = Column(Text, nullable=False)
    metadata_: dict | None = Column("metadata", JSON, nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    issue = relationship("Issue", back_populates="code_artifacts")
