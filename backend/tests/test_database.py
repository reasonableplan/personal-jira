from app.database import async_engine, async_session_factory, get_db
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class TestEngine:
    def test_engine_is_async(self) -> None:
        assert isinstance(async_engine, AsyncEngine)

    def test_engine_url_contains_asyncpg(self) -> None:
        assert "asyncpg" in str(async_engine.url)


class TestSessionFactory:
    def test_factory_type(self) -> None:
        assert isinstance(async_session_factory, async_sessionmaker)

    def test_factory_produces_async_session(self) -> None:
        session = async_session_factory()
        assert isinstance(session, AsyncSession)
        # cleanup
        import asyncio
        asyncio.get_event_loop().run_until_complete(session.close())


class TestGetDb:
    def test_get_db_is_async_generator(self) -> None:
        import inspect
        assert inspect.isasyncgenfunction(get_db)
