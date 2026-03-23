import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect

from app.models.agent import Agent, AgentStatus


class TestAgentStatus:
    def test_active_value(self):
        assert AgentStatus.ACTIVE == "active"

    def test_inactive_value(self):
        assert AgentStatus.INACTIVE == "inactive"

    def test_busy_value(self):
        assert AgentStatus.BUSY == "busy"


class TestAgentModel:
    def test_table_name(self):
        assert Agent.__tablename__ == "agents"

    def test_columns_exist(self):
        mapper = inspect(Agent)
        columns = {c.key for c in mapper.columns}
        expected = {"id", "name", "skills", "status", "current_issue_id", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_id_is_primary_key(self):
        mapper = inspect(Agent)
        pk_cols = [c.name for c in mapper.primary_key]
        assert "id" in pk_cols

    def test_name_not_nullable(self):
        col = Agent.__table__.columns["name"]
        assert col.nullable is False

    def test_name_unique(self):
        col = Agent.__table__.columns["name"]
        assert col.unique is True

    def test_skills_default_empty(self):
        agent = Agent(name="test-agent")
        assert agent.skills == []

    def test_status_default_active(self):
        agent = Agent(name="test-agent")
        assert agent.status == AgentStatus.ACTIVE

    def test_current_issue_id_nullable(self):
        col = Agent.__table__.columns["current_issue_id"]
        assert col.nullable is True

    def test_indexes(self):
        indexes = {idx.name for idx in Agent.__table__.indexes}
        assert "ix_agents_status" in indexes
        assert "ix_agents_name" in indexes
