from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

BASE_URL = "http://test/api/agents"


def _make_agent_row(
    agent_id: str = "agent-1",
    name: str = "Backend Agent",
    domain: str = "backend",
    status: str = "idle",
    current_task_id: str | None = None,
    last_heartbeat: datetime | None = None,
):
    class Row:
        pass

    r = Row()
    r.id = agent_id  # type: ignore[attr-defined]
    r.name = name  # type: ignore[attr-defined]
    r.domain = domain  # type: ignore[attr-defined]
    r.status = status  # type: ignore[attr-defined]
    r.current_task_id = current_task_id  # type: ignore[attr-defined]
    r.last_heartbeat = last_heartbeat  # type: ignore[attr-defined]
    return r


@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


class TestPostAgent:
    @pytest.mark.anyio
    async def test_create_agent_201(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        mock_db.execute = AsyncMock()
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none = AsyncMock(return_value=None)
        mock_db.execute.return_value = result_mock

        created = _make_agent_row()
        mock_db.get = AsyncMock(return_value=created)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.post(
                    "/", json={"id": "agent-1", "name": "Backend Agent", "domain": "backend"}
                )
            assert resp.status_code == 201
            data = resp.json()
            assert data["id"] == "agent-1"
            assert data["name"] == "Backend Agent"
            assert data["status"] == "idle"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_create_agent_duplicate_409(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        existing = _make_agent_row()
        result_mock = AsyncMock()
        result_mock.scalar_one_or_none = AsyncMock(return_value=existing)
        mock_db.execute = AsyncMock(return_value=result_mock)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.post(
                    "/", json={"id": "agent-1", "name": "Backend Agent", "domain": "backend"}
                )
            assert resp.status_code == 409
        finally:
            app.dependency_overrides.clear()


class TestGetAgents:
    @pytest.mark.anyio
    async def test_list_agents(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        agents = [_make_agent_row("a1"), _make_agent_row("a2", status="busy")]
        result_mock = AsyncMock()
        result_mock.scalars = lambda: AsyncMock(all=lambda: agents)
        mock_db.execute = AsyncMock(return_value=result_mock)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.get("/")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_list_agents_filter_status(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        agents = [_make_agent_row("a2", status="busy")]
        result_mock = AsyncMock()
        result_mock.scalars = lambda: AsyncMock(all=lambda: agents)
        mock_db.execute = AsyncMock(return_value=result_mock)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.get("/", params={"status": "busy"})
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()


class TestGetAgentDetail:
    @pytest.mark.anyio
    async def test_get_agent_200(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        agent = _make_agent_row(last_heartbeat=datetime.now(UTC))
        mock_db.get = AsyncMock(return_value=agent)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.get("/agent-1")
            assert resp.status_code == 200
            assert resp.json()["id"] == "agent-1"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_get_agent_404(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        mock_db.get = AsyncMock(return_value=None)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.get("/nonexistent")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_stale_heartbeat_shows_offline(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        stale_time = datetime.now(UTC) - timedelta(minutes=6)
        agent = _make_agent_row(status="idle", last_heartbeat=stale_time)
        mock_db.get = AsyncMock(return_value=agent)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.get("/agent-1")
            assert resp.status_code == 200
            assert resp.json()["status"] == "offline"
        finally:
            app.dependency_overrides.clear()


class TestHeartbeat:
    @pytest.mark.anyio
    async def test_heartbeat_200(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        agent = _make_agent_row()
        mock_db.get = AsyncMock(return_value=agent)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.patch("/agent-1/heartbeat", json={})
            assert resp.status_code == 200
            assert resp.json()["id"] == "agent-1"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_heartbeat_with_status(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        agent = _make_agent_row()
        mock_db.get = AsyncMock(return_value=agent)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.patch("/agent-1/heartbeat", json={"status": "busy"})
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.anyio
    async def test_heartbeat_404(self, mock_db: AsyncMock) -> None:
        from app.database import get_session

        mock_db.get = AsyncMock(return_value=None)

        async def override_get_session():
            yield mock_db

        app.dependency_overrides[get_session] = override_get_session
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url=BASE_URL
            ) as client:
                resp = await client.patch("/nonexistent/heartbeat", json={})
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()
