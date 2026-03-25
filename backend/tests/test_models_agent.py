from app.models.agent import Agent, AgentStatus
from app.models.base import Base


class TestAgentStatus:
    def test_values(self) -> None:
        assert AgentStatus.IDLE == "idle"
        assert AgentStatus.BUSY == "busy"
        assert AgentStatus.OFFLINE == "offline"


class TestAgentModel:
    def test_tablename(self) -> None:
        assert Agent.__tablename__ == "agents"

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Agent.__table__.columns}
        assert cols == {"id", "name", "domain", "status", "current_task_id", "last_heartbeat"}

    def test_pk_is_string(self) -> None:
        col = Agent.__table__.c.id
        assert col.primary_key

    def test_name_not_nullable(self) -> None:
        assert Agent.__table__.c.name.nullable is False

    def test_domain_not_nullable(self) -> None:
        assert Agent.__table__.c.domain.nullable is False

    def test_status_default(self) -> None:
        assert Agent.__table__.c.status.default.arg == AgentStatus.IDLE

    def test_current_task_id_fk(self) -> None:
        col = Agent.__table__.c.current_task_id
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "tasks.id"

    def test_current_task_id_nullable(self) -> None:
        assert Agent.__table__.c.current_task_id.nullable is True

    def test_last_heartbeat_nullable(self) -> None:
        assert Agent.__table__.c.last_heartbeat.nullable is True

    def test_status_index(self) -> None:
        idx_names = {idx.name for idx in Agent.__table__.indexes}
        assert "ix_agents_status" in idx_names

    def test_inherits_base(self) -> None:
        assert issubclass(Agent, Base)
