from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator

from personal_jira.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
