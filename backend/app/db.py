from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Session:  # type: ignore[misc]
    db = SessionLocal()
    try:
        yield db  # type: ignore[misc]
    finally:
        db.close()
