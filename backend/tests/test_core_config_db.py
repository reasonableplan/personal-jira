"""Tests for app.core.config and app.core.database modules."""

from collections.abc import AsyncGenerator

import pytest
from app.core.config import Settings, settings
from app.core.database import async_session_factory, engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession


class TestSettings:
    def test_settings_instance_exists(self) -> None:
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_database_url_default(self) -> None:
        assert "postgresql+asyncpg://" in settings.DATABASE_URL
        assert "5433" in settings.DATABASE_URL

    def test_app_name_default(self) -> None:
        assert settings.APP_NAME == "Personal Jira"

    def test_debug_default(self) -> None:
        assert settings.DEBUG is False

    def test_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("DEBUG", "true")
        s = Settings()
        assert s.APP_NAME == "Test App"
        assert s.DEBUG is True


class TestDatabase:
    def test_engine_created(self) -> None:
        assert engine is not None

    def test_async_session_factory_created(self) -> None:
        assert async_session_factory is not None

    def test_get_db_returns_async_generator(self) -> None:
        gen = get_db()
        assert isinstance(gen, AsyncGenerator)

    @pytest.mark.asyncio
    async def test_get_db_yields_async_session(self) -> None:
        """get_db yields an AsyncSession (does not require a live DB connection)."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break


class TestReExports:
    """Verify that the legacy import paths (app.config, app.database) work."""

    def test_config_reexport(self) -> None:
        from app.config import settings as s
        assert s is settings

    def test_database_reexport(self) -> None:
        from app.database import get_db as gdb
        assert gdb is get_db
