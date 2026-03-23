from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


class TestFixtures:
    async def test_async_engine_fixture(self, async_engine) -> None:
        assert isinstance(async_engine, AsyncEngine)

    async def test_db_session_fixture(self, db_session) -> None:
        assert isinstance(db_session, AsyncSession)

    async def test_client_fixture(self, client) -> None:
        assert isinstance(client, AsyncClient)

    async def test_client_can_reach_health(self, client) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
