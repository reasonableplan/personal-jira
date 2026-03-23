import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from personal_jira.models.base import Base


class BundleItemType(str, enum.Enum):
    FILE = "file"
    SPEC = "spec"
    SNIPPET = "snippet"


class ContextBundle(Base):
    __tablename__ = "context_bundles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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

    items = relationship(
        "BundleItem",
        back_populates="bundle",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    issue = relationship("Issue", back_populates="context_bundles")


class BundleItem(Base):
    __tablename__ = "bundle_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    bundle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("context_bundles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_type = Column(
        Enum(BundleItemType, name="bundle_item_type"),
        nullable=False,
    )
    path = Column(String(1024), nullable=True)
    content = Column(Text, nullable=True)
    line_start = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)

    bundle = relationship("ContextBundle", back_populates="items")
