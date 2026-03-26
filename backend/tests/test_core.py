"""app.core.config 및 app.core.database 모듈 테스트."""

import pytest
from app.core.config import Settings, settings
from app.core.database import Base, async_session_factory, engine, get_db
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestSettings:
    def test_app_name(self) -> None:
        assert settings.APP_NAME == "Personal Jira"

    def test_debug_default_false(self) -> None:
        assert settings.DEBUG is False

    def test_database_url_uses_asyncpg(self) -> None:
        assert "asyncpg" in settings.DATABASE_URL

    def test_settings_instance(self) -> None:
        assert isinstance(settings, Settings)


class TestDatabase:
    def test_engine_is_async(self) -> None:
        assert isinstance(engine, AsyncEngine)

    def test_session_factory_expire_on_commit_false(self) -> None:
        assert async_session_factory.kw.get("expire_on_commit") is False

    def test_base_is_declarative(self) -> None:
        assert hasattr(Base, "metadata")

    @pytest.mark.asyncio
    async def test_get_db_yields_async_session(self) -> None:
        gen = get_db()
        session = await gen.__anext__()
        try:
            assert isinstance(session, AsyncSession)
        finally:
            await gen.aclose()


class TestBackwardCompatImports:
    """app.database, app.config에서의 re-export 확인."""

    def test_import_from_app_database(self) -> None:
        from app.database import Base as B
        from app.database import get_db as gdb

        assert B is Base
        assert gdb is get_db

    def test_import_from_app_config(self) -> None:
        from app.config import settings as s

        assert s is settings
