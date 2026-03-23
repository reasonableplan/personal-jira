import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.agent import Agent, AgentStatus
from app.models.issue import Issue, IssueStatus
from app.schemas.claim import ClaimRequest, ClaimResponse
from app.services.claim import ClaimService
from app.services.exceptions import AgentNotFoundError, AgentSkillMismatchError


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def service(mock_db):
    return ClaimService(mock_db)


class TestClaimIssue:
    @pytest.mark.asyncio
    async def test_claim_success(self, service, mock_db):
        agent_id = uuid.uuid4()
        issue_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1", skills=["python"], status=AgentStatus.ACTIVE)
        issue = Issue(id=issue_id, title="task", status=IssueStatus.READY, required_skills=[])
        mock_db.execute = AsyncMock(side_effect=[
            MagicMock(scalar_one_or_none=MagicMock(return_value=agent)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=issue)),
        ])
        result = await service.claim(ClaimRequest(agent_id=agent_id))
        assert result is not None
        mock_db.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_claim_no_ready_issue(self, service, mock_db):
        agent_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1", skills=["python"], status=AgentStatus.ACTIVE)
        mock_db.execute = AsyncMock(side_effect=[
            MagicMock(scalar_one_or_none=MagicMock(return_value=agent)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        ])
        result = await service.claim(ClaimRequest(agent_id=agent_id))
        assert result is None

    @pytest.mark.asyncio
    async def test_claim_agent_not_found(self, service, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(AgentNotFoundError):
            await service.claim(ClaimRequest(agent_id=uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_claim_skills_matching(self, service, mock_db):
        agent_id = uuid.uuid4()
        issue_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1", skills=["python", "fastapi"], status=AgentStatus.ACTIVE)
        issue = Issue(id=issue_id, title="task", status=IssueStatus.READY, required_skills=["python"])
        mock_db.execute = AsyncMock(side_effect=[
            MagicMock(scalar_one_or_none=MagicMock(return_value=agent)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=issue)),
        ])
        result = await service.claim(ClaimRequest(agent_id=agent_id))
        assert result is not None

    @pytest.mark.asyncio
    async def test_claim_busy_agent_rejected(self, service, mock_db):
        agent_id = uuid.uuid4()
        agent = Agent(id=agent_id, name="agent-1", skills=[], status=AgentStatus.BUSY)
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=agent)))
        with pytest.raises(AgentSkillMismatchError, match="busy"):
            await service.claim(ClaimRequest(agent_id=agent_id))
