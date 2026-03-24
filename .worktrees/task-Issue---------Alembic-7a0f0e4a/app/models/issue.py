from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

STATUS_DEFAULT = "todo"
PRIORITY_DEFAULT = "medium"
TITLE_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 20
PRIORITY_MAX_LENGTH = 20


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(STATUS_MAX_LENGTH), default=STATUS_DEFAULT, server_default=STATUS_DEFAULT, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(PRIORITY_MAX_LENGTH), default=PRIORITY_DEFAULT, server_default=PRIORITY_DEFAULT, index=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
