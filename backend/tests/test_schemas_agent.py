from datetime import datetime

import pytest
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from pydantic import ValidationError


class TestAgentCreate:
    def test_valid(self) -> None:
        data = AgentCreate(id="agent-1", name="Backend Agent", domain="backend")
        assert data.id == "agent-1"
        assert data.name == "Backend Agent"
        assert data.domain == "backend"

    def test_missing_id(self) -> None:
        with pytest.raises(ValidationError):
            AgentCreate(name="Backend Agent", domain="backend")  # type: ignore[call-arg]

    def test_missing_name(self) -> None:
        with pytest.raises(ValidationError):
            AgentCreate(id="agent-1", domain="backend")  # type: ignore[call-arg]

    def test_missing_domain(self) -> None:
        with pytest.raises(ValidationError):
            AgentCreate(id="agent-1", name="Backend Agent")  # type: ignore[call-arg]


class TestAgentUpdate:
    def test_all_optional(self) -> None:
        data = AgentUpdate()
        assert data.status is None

    def test_with_status(self) -> None:
        data = AgentUpdate(status="busy")
        assert data.status == "busy"


class TestAgentResponse:
    def test_valid(self) -> None:
        now = datetime.now().isoformat()
        data = AgentResponse(
            id="agent-1",
            name="Backend Agent",
            domain="backend",
            status="idle",
            last_heartbeat=now,
        )
        assert data.id == "agent-1"
        assert data.status == "idle"

    def test_nullable_heartbeat(self) -> None:
        data = AgentResponse(
            id="agent-1",
            name="Backend Agent",
            domain="backend",
            status="idle",
            last_heartbeat=None,
        )
        assert data.last_heartbeat is None
