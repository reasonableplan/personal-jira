from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.database import async_session_factory, engine


def test_engine_is_async() -> None:
    assert isinstance(engine, AsyncEngine)


def test_session_factory_type() -> None:
    assert isinstance(async_session_factory, async_sessionmaker)


def test_engine_url_matches_config() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    assert str(engine.url) == settings.DATABASE_URL


async def test_get_db_yields_session() -> None:
    from app.core.database import get_db

    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass
