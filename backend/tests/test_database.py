from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from personal_jira.database import async_engine, get_db


class TestDatabaseEngine:
    def test_engine_is_async(self) -> None:
        assert isinstance(async_engine, AsyncEngine)


class TestGetDb:
    async def test_get_db_yields_session(self) -> None:
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break
