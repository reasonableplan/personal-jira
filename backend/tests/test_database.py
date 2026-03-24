from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.database import async_session_factory, engine


class TestDatabaseSetup:
    def test_engine_is_async(self) -> None:
        assert isinstance(engine, AsyncEngine)

    def test_session_factory_type(self) -> None:
        assert isinstance(async_session_factory, async_sessionmaker)

    def test_engine_url_contains_asyncpg(self) -> None:
        assert "asyncpg" in str(engine.url)
