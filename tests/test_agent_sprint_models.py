import uuid
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from personal_jira.models.agent import Agent, AgentStatus
from personal_jira.models.sprint import Sprint
from personal_jira.models.work_log import WorkLog
from personal_jira.models.code_artifact import CodeArtifact, ArtifactType
from personal_jira.models.base import Base


@pytest.fixture
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(async_engine):
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:
        yield sess


class TestAgentModelSchema:
    def test_table_name(self):
        assert Agent.__tablename__ == "agents"

    def test_columns_exist(self):
        mapper = inspect(Agent)
        columns = {c.key for c in mapper.columns}
        assert {"id", "name", "skills", "status", "created_at", "updated_at"}.issubset(columns)

    def test_id_is_primary_key(self):
        mapper = inspect(Agent)
        pk_cols = [c.key for c in mapper.columns if c.primary_key]
        assert "id" in pk_cols

    def test_name_not_nullable(self):
        mapper = inspect(Agent)
        name_col = mapper.columns["name"]
        assert not name_col.nullable

    def test_name_unique(self):
        mapper = inspect(Agent)
        name_col = mapper.columns["name"]
        assert name_col.unique

    def test_status_default(self):
        agent = Agent(name="test-agent")
        assert agent.status == AgentStatus.IDLE

    def test_skills_default(self):
        agent = Agent(name="test-agent")
        assert agent.skills == []


class TestAgentStatus:
    def test_idle_value(self):
        assert AgentStatus.IDLE == "idle"

    def test_busy_value(self):
        assert AgentStatus.BUSY == "busy"

    def test_offline_value(self):
        assert AgentStatus.OFFLINE == "offline"

    def test_error_value(self):
        assert AgentStatus.ERROR == "error"


class TestAgentCRUD:
    @pytest.mark.asyncio
    async def test_create_agent(self, session: AsyncSession):
        agent = Agent(name="agent-backend", skills=["python", "fastapi"], status=AgentStatus.IDLE)
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        assert agent.id is not None
        assert agent.name == "agent-backend"
        assert agent.skills == ["python", "fastapi"]
        assert agent.status == AgentStatus.IDLE
        assert agent.created_at is not None
        assert agent.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_agent_minimal(self, session: AsyncSession):
        agent = Agent(name="agent-minimal")
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        assert agent.id is not None
        assert agent.skills == []
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_unique_name_constraint(self, session: AsyncSession):
        a1 = Agent(name="agent-dup")
        a2 = Agent(name="agent-dup")
        session.add(a1)
        await session.commit()
        session.add(a2)
        with pytest.raises(Exception):
            await session.commit()


class TestSprintModelSchema:
    def test_table_name(self):
        assert Sprint.__tablename__ == "sprints"

    def test_columns_exist(self):
        mapper = inspect(Sprint)
        columns = {c.key for c in mapper.columns}
        assert {"id", "name", "start_date", "end_date", "goal", "created_at", "updated_at"}.issubset(columns)

    def test_name_not_nullable(self):
        mapper = inspect(Sprint)
        assert not mapper.columns["name"].nullable

    def test_start_date_not_nullable(self):
        mapper = inspect(Sprint)
        assert not mapper.columns["start_date"].nullable

    def test_end_date_not_nullable(self):
        mapper = inspect(Sprint)
        assert not mapper.columns["end_date"].nullable

    def test_goal_nullable(self):
        mapper = inspect(Sprint)
        assert mapper.columns["goal"].nullable


class TestSprintCRUD:
    @pytest.mark.asyncio
    async def test_create_sprint(self, session: AsyncSession):
        sprint = Sprint(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
            goal="MVP 완성",
        )
        session.add(sprint)
        await session.commit()
        await session.refresh(sprint)
        assert sprint.id is not None
        assert sprint.name == "Sprint 1"
        assert sprint.start_date == date(2026, 3, 23)
        assert sprint.end_date == date(2026, 4, 6)
        assert sprint.goal == "MVP 완성"

    @pytest.mark.asyncio
    async def test_create_sprint_without_goal(self, session: AsyncSession):
        sprint = Sprint(name="Sprint 2", start_date=date(2026, 4, 7), end_date=date(2026, 4, 20))
        session.add(sprint)
        await session.commit()
        await session.refresh(sprint)
        assert sprint.goal is None


class TestWorkLogModelSchema:
    def test_table_name(self):
        assert WorkLog.__tablename__ == "work_logs"

    def test_columns_exist(self):
        mapper = inspect(WorkLog)
        columns = {c.key for c in mapper.columns}
        assert {"id", "issue_id", "agent_id", "llm_calls", "tokens_used", "content", "created_at", "updated_at"}.issubset(columns)

    def test_llm_calls_default(self):
        wl = WorkLog(issue_id=uuid.uuid4(), agent_id=uuid.uuid4())
        assert wl.llm_calls == 0

    def test_tokens_used_default(self):
        wl = WorkLog(issue_id=uuid.uuid4(), agent_id=uuid.uuid4())
        assert wl.tokens_used == 0

    def test_issue_id_not_nullable(self):
        mapper = inspect(WorkLog)
        assert not mapper.columns["issue_id"].nullable

    def test_agent_id_not_nullable(self):
        mapper = inspect(WorkLog)
        assert not mapper.columns["agent_id"].nullable

    def test_has_issue_id_index(self):
        mapper = inspect(WorkLog)
        assert mapper.columns["issue_id"].index

    def test_has_agent_id_index(self):
        mapper = inspect(WorkLog)
        assert mapper.columns["agent_id"].index


class TestWorkLogCRUD:
    @pytest.mark.asyncio
    async def test_create_work_log(self, session: AsyncSession):
        agent = Agent(name="agent-wl")
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        issue_id = uuid.uuid4()
        wl = WorkLog(
            issue_id=issue_id,
            agent_id=agent.id,
            llm_calls=5,
            tokens_used=12000,
            content="Implemented feature X",
        )
        session.add(wl)
        await session.commit()
        await session.refresh(wl)
        assert wl.id is not None
        assert wl.llm_calls == 5
        assert wl.tokens_used == 12000
        assert wl.content == "Implemented feature X"

    @pytest.mark.asyncio
    async def test_create_work_log_defaults(self, session: AsyncSession):
        agent = Agent(name="agent-wl-def")
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        wl = WorkLog(issue_id=uuid.uuid4(), agent_id=agent.id)
        session.add(wl)
        await session.commit()
        await session.refresh(wl)
        assert wl.llm_calls == 0
        assert wl.tokens_used == 0
        assert wl.content is None


class TestCodeArtifactModelSchema:
    def test_table_name(self):
        assert CodeArtifact.__tablename__ == "code_artifacts"

    def test_columns_exist(self):
        mapper = inspect(CodeArtifact)
        columns = {c.key for c in mapper.columns}
        assert {"id", "issue_id", "agent_id", "artifact_type", "files", "commit_sha", "pr_url", "created_at", "updated_at"}.issubset(columns)

    def test_issue_id_not_nullable(self):
        mapper = inspect(CodeArtifact)
        assert not mapper.columns["issue_id"].nullable

    def test_commit_sha_nullable(self):
        mapper = inspect(CodeArtifact)
        assert mapper.columns["commit_sha"].nullable

    def test_pr_url_nullable(self):
        mapper = inspect(CodeArtifact)
        assert mapper.columns["pr_url"].nullable

    def test_has_issue_id_index(self):
        mapper = inspect(CodeArtifact)
        assert mapper.columns["issue_id"].index

    def test_has_agent_id_index(self):
        mapper = inspect(CodeArtifact)
        assert mapper.columns["agent_id"].index


class TestArtifactType:
    def test_code_value(self):
        assert ArtifactType.CODE == "code"

    def test_test_value(self):
        assert ArtifactType.TEST == "test"

    def test_config_value(self):
        assert ArtifactType.CONFIG == "config"

    def test_docs_value(self):
        assert ArtifactType.DOCS == "docs"


class TestCodeArtifactCRUD:
    @pytest.mark.asyncio
    async def test_create_artifact(self, session: AsyncSession):
        agent = Agent(name="agent-art")
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        issue_id = uuid.uuid4()
        artifact = CodeArtifact(
            issue_id=issue_id,
            agent_id=agent.id,
            artifact_type=ArtifactType.CODE,
            files=["src/main.py", "src/utils.py"],
            commit_sha="abc123def456",
            pr_url="https://github.com/org/repo/pull/1",
        )
        session.add(artifact)
        await session.commit()
        await session.refresh(artifact)
        assert artifact.id is not None
        assert artifact.files == ["src/main.py", "src/utils.py"]
        assert artifact.commit_sha == "abc123def456"
        assert artifact.pr_url == "https://github.com/org/repo/pull/1"
        assert artifact.artifact_type == ArtifactType.CODE

    @pytest.mark.asyncio
    async def test_create_artifact_minimal(self, session: AsyncSession):
        agent = Agent(name="agent-art-min")
        session.add(agent)
        await session.commit()
        await session.refresh(agent)

        artifact = CodeArtifact(
            issue_id=uuid.uuid4(),
            agent_id=agent.id,
            artifact_type=ArtifactType.TEST,
            files=["tests/test_foo.py"],
        )
        session.add(artifact)
        await session.commit()
        await session.refresh(artifact)
        assert artifact.commit_sha is None
        assert artifact.pr_url is None
