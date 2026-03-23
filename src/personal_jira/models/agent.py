import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from personal_jira.database import Base


class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class TaskResult(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, unique=True)
    role = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default=AgentStatus.IDLE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tasks = relationship("AgentTask", back_populates="agent")

    __table_args__ = (
        Index("ix_agents_status", "status"),
    )


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    result = Column(String(30), nullable=False, default=TaskResult.IN_PROGRESS)
    attempt_count = Column(Integer, nullable=False, default=1)
    review_count = Column(Integer, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    agent = relationship("Agent", back_populates="tasks")
    issue = relationship("Issue")
    work_logs = relationship("WorkLog", back_populates="agent_task", cascade="all, delete-orphan")
    artifacts = relationship("CodeArtifact", back_populates="agent_task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_agent_tasks_agent_id", "agent_id"),
        Index("ix_agent_tasks_issue_id", "issue_id"),
        Index("ix_agent_tasks_result", "result"),
    )
