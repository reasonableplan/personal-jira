import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.core.database import async_session_factory, engine, get_db


def test_engine_is_async_engine() -> None:
    assert isinstance(engine, AsyncEngine)


def test_session_factory_is_async_sessionmaker() -> None:
    assert isinstance(async_session_factory, async_sessionmaker)


@pytest.mark.asyncio
async def test_get_db_yields_session() -> None:
    gen = get_db()
    session = await gen.__anext__()
    assert session is not None
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass
