from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_engine = create_async_engine(settings.DATABASE_URL)
_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_engine():
    return _engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_factory() as session:
        yield session
