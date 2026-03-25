from app.database import Base, async_session_factory, engine, get_session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class TestDatabaseSetup:
    def test_engine_is_async(self) -> None:
        assert isinstance(engine, AsyncEngine)

    def test_engine_url_matches_config(self) -> None:
        from app.config import settings
        assert str(engine.url) == settings.database_url

    def test_session_factory_type(self) -> None:
        assert isinstance(async_session_factory, async_sessionmaker)

    def test_base_exists(self) -> None:
        assert hasattr(Base, "metadata")

    async def test_get_session_is_async_generator(self) -> None:
        gen = get_session()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
