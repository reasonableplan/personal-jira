import inspect

from app.config import settings
from app.database import Base, async_engine, async_session_factory, get_db


def test_engine_is_configured() -> None:
    assert async_engine is not None
    assert "asyncpg" in str(async_engine.url.drivername) or "aiosqlite" in str(
        async_engine.url.drivername
    )


def test_engine_echo_matches_config() -> None:
    assert async_engine.echo == settings.ECHO_SQL


def test_session_factory_configured() -> None:
    assert async_session_factory is not None


def test_base_has_metadata() -> None:
    assert Base.metadata is not None


def test_get_db_is_async_generator() -> None:
    assert inspect.isasyncgenfunction(get_db)
