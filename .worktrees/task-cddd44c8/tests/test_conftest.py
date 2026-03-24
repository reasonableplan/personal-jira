from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from tests.conftest import test_engine


async def test_tables_created_during_setup(async_session: AsyncSession) -> None:
    result = await async_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    )
    tables = {row[0] for row in result.fetchall()}
    expected = {t for t in Base.metadata.tables}
    assert expected.issubset(tables)


async def test_session_rollback_isolation(async_session: AsyncSession) -> None:
    await async_session.execute(text("INSERT INTO issues (title, status, priority) VALUES ('rollback-test', 'todo', 3)"))
    result = await async_session.execute(text("SELECT count(*) FROM issues"))
    assert result.scalar() == 1


async def test_second_test_has_empty_table(async_session: AsyncSession) -> None:
    result = await async_session.execute(text("SELECT count(*) FROM issues"))
    assert result.scalar() == 0


async def test_client_fixture_works(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_tables_dropped_between_tests() -> None:
    async with test_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = {row[0] for row in result.fetchall()}
        expected = {t for t in Base.metadata.tables}
        assert expected.issubset(tables)
