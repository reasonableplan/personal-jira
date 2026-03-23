import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.database import get_db
from app.models.agent import Agent, AgentStatus


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
async def client(app, mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class TestCreateAgentEndpoint:
    @pytest.mark.asyncio
    async def test_create_201(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            agent_id = uuid.uuid4()
            mock_svc = AsyncMock()
            mock_svc.create.return_value = Agent(
                id=agent_id, name="agent-1", skills=["python"],
                status=AgentStatus.ACTIVE, current_issue_id=None,
            )
            MockSvc.return_value = mock_svc
            resp = await client.post("/api/v1/agents", json={"name": "agent-1", "skills": ["python"]})
            assert resp.status_code == 201
            assert resp.json()["name"] == "agent-1"

    @pytest.mark.asyncio
    async def test_create_409_duplicate(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            from app.services.exceptions import AgentNameConflictError
            mock_svc = AsyncMock()
            mock_svc.create.side_effect = AgentNameConflictError("agent-1")
            MockSvc.return_value = mock_svc
            resp = await client.post("/api/v1/agents", json={"name": "agent-1"})
            assert resp.status_code == 409


class TestGetAgentEndpoint:
    @pytest.mark.asyncio
    async def test_get_200(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            agent_id = uuid.uuid4()
            mock_svc = AsyncMock()
            mock_svc.get.return_value = Agent(
                id=agent_id, name="agent-1", skills=[],
                status=AgentStatus.ACTIVE, current_issue_id=None,
            )
            MockSvc.return_value = mock_svc
            resp = await client.get(f"/api/v1/agents/{agent_id}")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_404(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            from app.services.exceptions import AgentNotFoundError
            mock_svc = AsyncMock()
            mock_svc.get.side_effect = AgentNotFoundError(uuid.uuid4())
            MockSvc.return_value = mock_svc
            resp = await client.get(f"/api/v1/agents/{uuid.uuid4()}")
            assert resp.status_code == 404


class TestListAgentsEndpoint:
    @pytest.mark.asyncio
    async def test_list_200(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            mock_svc = AsyncMock()
            mock_svc.list.return_value = []
            MockSvc.return_value = mock_svc
            resp = await client.get("/api/v1/agents")
            assert resp.status_code == 200
            assert resp.json() == []


class TestDeleteAgentEndpoint:
    @pytest.mark.asyncio
    async def test_delete_204(self, client):
        with patch("app.api.agents.AgentService") as MockSvc:
            mock_svc = AsyncMock()
            mock_svc.delete.return_value = None
            MockSvc.return_value = mock_svc
            resp = await client.delete(f"/api/v1/agents/{uuid.uuid4()}")
            assert resp.status_code == 204


class TestClaimEndpoint:
    @pytest.mark.asyncio
    async def test_claim_200(self, client):
        with patch("app.api.claim.ClaimService") as MockSvc:
            issue_id = uuid.uuid4()
            mock_svc = AsyncMock()
            mock_svc.claim.return_value = type("Obj", (), {
                "id": issue_id, "title": "task", "status": "in_progress",
                "assignee": "agent-1", "priority": "medium",
            })()
            MockSvc.return_value = mock_svc
            resp = await client.post("/api/v1/issues/claim", json={"agent_id": str(uuid.uuid4())})
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_claim_204_no_issue(self, client):
        with patch("app.api.claim.ClaimService") as MockSvc:
            mock_svc = AsyncMock()
            mock_svc.claim.return_value = None
            MockSvc.return_value = mock_svc
            resp = await client.post("/api/v1/issues/claim", json={"agent_id": str(uuid.uuid4())})
            assert resp.status_code == 204
