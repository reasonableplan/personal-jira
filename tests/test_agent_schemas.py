import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse


class TestAgentCreate:
    def test_valid_create(self):
        data = AgentCreate(name="agent-1", skills=["python", "fastapi"])
        assert data.name == "agent-1"
        assert data.skills == ["python", "fastapi"]

    def test_minimal_create(self):
        data = AgentCreate(name="agent-1")
        assert data.skills == []

    def test_name_required(self):
        with pytest.raises(ValidationError):
            AgentCreate()

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            AgentCreate(name="")

    def test_name_max_length(self):
        with pytest.raises(ValidationError):
            AgentCreate(name="a" * 256)

    def test_skills_normalized_lowercase(self):
        data = AgentCreate(name="agent-1", skills=["Python", "FastAPI"])
        assert data.skills == ["python", "fastapi"]

    def test_skills_deduplicated(self):
        data = AgentCreate(name="agent-1", skills=["python", "Python", "PYTHON"])
        assert data.skills == ["python"]


class TestAgentUpdate:
    def test_all_optional(self):
        data = AgentUpdate()
        assert data.name is None
        assert data.skills is None

    def test_partial_update(self):
        data = AgentUpdate(skills=["go"])
        assert data.name is None
        assert data.skills == ["go"]

    def test_skills_normalized(self):
        data = AgentUpdate(skills=["Go", "RUST"])
        assert data.skills == ["go", "rust"]


class TestAgentResponse:
    def test_from_attributes(self):
        now = datetime.now(timezone.utc)
        agent_id = uuid.uuid4()
        data = AgentResponse(
            id=agent_id,
            name="agent-1",
            skills=["python"],
            status="active",
            current_issue_id=None,
            created_at=now,
            updated_at=now,
        )
        assert data.id == agent_id
        assert data.status == "active"
