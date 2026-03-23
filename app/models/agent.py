import enum
import uuid as _uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Enum, Index, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    skills = Column(ARRAY(String), nullable=False, default=list)
    status = Column(
        Enum(AgentStatus, name="agent_status", create_constraint=True),
        nullable=False,
        default=AgentStatus.ACTIVE,
    )
    current_issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_agents_status", "status"),
        Index("ix_agents_name", "name"),
    )
