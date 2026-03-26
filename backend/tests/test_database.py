"""Tests for core database and config modules."""

from collections.abc import AsyncGenerator

from app.core.config import Settings, settings
from app.core.database import Base, async_session_factory, engine, get_db


def test_settings_has_database_url() -> None:
    assert isinstance(settings, Settings)
    assert "postgresql+asyncpg://" in settings.DATABASE_URL


def test_settings_app_name() -> None:
    assert settings.APP_NAME == "Personal Jira"


def test_settings_debug_default() -> None:
    assert settings.DEBUG is False


def test_base_is_declarative_base() -> None:
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_engine_is_async() -> None:
    assert engine is not None
    assert "asyncpg" in str(engine.url)


def test_session_factory_configured() -> None:
    assert async_session_factory is not None


def test_get_db_returns_async_generator() -> None:
    gen = get_db()
    assert isinstance(gen, AsyncGenerator)


def test_import_from_app_config() -> None:
    """from app.config import settings should work."""
    from app.config import settings as s

    assert s is settings


def test_import_from_app_database() -> None:
    """from app.database import get_db should work."""
    from app.database import get_db as gdb

    assert gdb is get_db
