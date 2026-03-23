import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.agent import Agent, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.agent import AgentService
from app.services.exceptions import AgentNotFoundError, AgentNameConflictError


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def service(mock_db):
    return AgentService(mock_db)


class TestCreateAgent:
    @pytest.mark.asyncio
    async def test_create_success(self, service, mock_db):
        req = AgentCreate(name="agent-1", skills=["python"])
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        mock_db.refresh = AsyncMock()
        result = await service.create(req)
        assert result.name == "agent-1"
        assert result.skills == ["python"]
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_duplicate_name(self, service, mock_db):
        req = AgentCreate(name="agent-1", skills=["python"])
        existing = Agent(id=uuid.uuid4(), name="agent-1")
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing)))
        with pytest.raises(AgentNameConflictError):
            await service.create(req)


class TestGetAgent:
    @pytest.mark.asyncio
    async def test_get_found(self, service, mock_db):
        agent_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1")
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=agent)))
        result = await service.get(agent_id)
        assert result.name == "agent-1"

    @pytest.mark.asyncio
    async def test_get_not_found(self, service, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(AgentNotFoundError):
            await service.get(uuid.uuid4())


class TestListAgents:
    @pytest.mark.asyncio
    async def test_list_empty(self, service, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
        result = await service.list()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_with_status_filter(self, service, mock_db):
        agents = [Agent(id=uuid.uuid4(), name="a1", status=AgentStatus.ACTIVE)]
        mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=agents)))))
        result = await service.list(status=AgentStatus.ACTIVE)
        assert len(result) == 1


class TestUpdateAgent:
    @pytest.mark.asyncio
    async def test_update_partial(self, service, mock_db):
        agent_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1", skills=["python"])
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=agent)))
        req = AgentUpdate(skills=["go", "rust"])
        result = await service.update(agent_id, req)
        assert result.skills == ["go", "rust"]

    @pytest.mark.asyncio
    async def test_update_not_found(self, service, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(AgentNotFoundError):
            await service.update(uuid.uuid4(), AgentUpdate(name="new"))


class TestDeleteAgent:
    @pytest.mark.asyncio
    async def test_delete_success(self, service, mock_db):
        agent_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1")
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=agent)))
        await service.delete(agent_id)
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, service, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(AgentNotFoundError):
            await service.delete(uuid.uuid4())
