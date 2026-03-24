import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


async def test_db_session_is_async(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


async def test_db_session_creates_tables(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name='issues'")
    )
    assert result.scalar() == "issues"


async def test_db_session_rollback_isolation(db_session: AsyncSession) -> None:
    await db_session.execute(
        text("INSERT INTO issues (title, status, priority) VALUES ('Isolation test', 'todo', 'medium')")
    )
    await db_session.flush()
    result = await db_session.execute(text("SELECT COUNT(*) FROM issues"))
    assert result.scalar() == 1


async def test_db_session_rollback_verified(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT COUNT(*) FROM issues"))
    assert result.scalar() == 0


async def test_client_is_async(client: AsyncClient) -> None:
    assert isinstance(client, AsyncClient)
    assert str(client.base_url) == "http://test/"


async def test_client_uses_test_db(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.get("/nonexistent-route")
    assert response.status_code in (404, 405)
