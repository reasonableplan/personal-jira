import enum
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from personal_jira.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from personal_jira.models.work_log import WorkLog
    from personal_jira.models.code_artifact import CodeArtifact


class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    skills: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[str] = mapped_column(
        String(20), default=AgentStatus.IDLE, nullable=False
    )

    work_logs: Mapped[List["WorkLog"]] = relationship(back_populates="agent", cascade="all, delete-orphan")
    code_artifacts: Mapped[List["CodeArtifact"]] = relationship(back_populates="agent", cascade="all, delete-orphan")
