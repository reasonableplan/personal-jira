import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from personal_jira.database import Base
from personal_jira.models.agent import Agent, AgentTask, AgentStatus, TaskResult
from personal_jira.models.issue import Issue, IssueStatus, IssueType, IssuePriority
from personal_jira.models.work_log import WorkLog
from personal_jira.models.code_artifact import CodeArtifact, ArtifactType
from personal_jira.services.agent_service import AgentService
from personal_jira.config import settings

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as sess:
        yield sess


@pytest.fixture
async def agent_service(session: AsyncSession) -> AgentService:
    return AgentService(session)


@pytest.fixture
async def sample_agent(session: AsyncSession) -> Agent:
    agent = Agent(name="agent-backend", role="backend", status=AgentStatus.IDLE)
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@pytest.fixture
async def sample_issue(session: AsyncSession) -> Issue:
    issue = Issue(
        title="Test issue",
        issue_type=IssueType.TASK,
        status=IssueStatus.TODO,
        priority=IssuePriority.MEDIUM,
    )
    session.add(issue)
    await session.commit()
    await session.refresh(issue)
    return issue


class TestAutoPreemption:
    async def test_claim_task_assigns_agent(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        assert task is not None
        assert task.agent_id == sample_agent.id
        assert task.issue_id == sample_issue.id
        assert task.result == TaskResult.IN_PROGRESS

    async def test_claim_already_claimed_task_returns_none(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        agent2 = Agent(name="agent-frontend", role="frontend", status=AgentStatus.IDLE)
        session.add(agent2)
        await session.commit()
        await session.refresh(agent2)

        await agent_service.claim_task(sample_agent.id, sample_issue.id)
        result = await agent_service.claim_task(agent2.id, sample_issue.id)
        assert result is None

    async def test_concurrent_claims_only_one_succeeds(self, session: AsyncSession, sample_issue: Issue):
        agents = []
        for i in range(3):
            a = Agent(name=f"agent-{i}", role="backend", status=AgentStatus.IDLE)
            session.add(a)
        await session.commit()

        stmt = select(Agent)
        result = await session.execute(stmt)
        agents = result.scalars().all()

        service = AgentService(session)
        results = []
        for agent in agents:
            r = await service.claim_task(agent.id, sample_issue.id)
            results.append(r)

        successful = [r for r in results if r is not None]
        assert len(successful) == 1

    async def test_agent_status_changes_to_busy_on_claim(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await session.refresh(sample_agent)
        assert sample_agent.status == AgentStatus.BUSY


class TestWorkLog:
    async def test_create_work_log(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        log = await agent_service.add_work_log(
            task_id=task.id,
            summary="Implemented feature X",
            llm_calls=5,
            tokens_used=1200,
        )
        assert log.id is not None
        assert log.issue_id == sample_issue.id
        assert log.agent_id == sample_agent.id
        assert log.llm_calls == 5
        assert log.tokens_used == 1200

    async def test_work_log_default_values(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        log = await agent_service.add_work_log(task_id=task.id, summary="Basic work")
        assert log.llm_calls == 0
        assert log.tokens_used == 0

    async def test_list_work_logs_for_task(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.add_work_log(task_id=task.id, summary="Step 1")
        await agent_service.add_work_log(task_id=task.id, summary="Step 2")
        logs = await agent_service.get_work_logs(task.id)
        assert len(logs) == 2


class TestFailureRetry:
    async def test_fail_task_sets_result(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        updated = await agent_service.fail_task(task.id, error_message="Compilation error")
        assert updated.result == TaskResult.FAILED
        assert updated.error_message == "Compilation error"

    async def test_fail_task_increments_attempt_count(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.fail_task(task.id, error_message="Error")
        await session.refresh(task)
        assert task.attempt_count == 1

    async def test_retry_task_creates_new_attempt(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.fail_task(task.id, error_message="Error")
        new_task = await agent_service.retry_task(task.id)
        assert new_task is not None
        assert new_task.id != task.id
        assert new_task.attempt_count == 2
        assert new_task.result == TaskResult.IN_PROGRESS

    async def test_retry_exceeds_max_attempts_returns_none(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        task.attempt_count = settings.MAX_RETRY_ATTEMPTS
        await session.commit()
        await agent_service.fail_task(task.id, error_message="Error")
        result = await agent_service.retry_task(task.id)
        assert result is None

    async def test_agent_returns_to_idle_after_failure(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.fail_task(task.id, error_message="Error")
        await session.refresh(sample_agent)
        assert sample_agent.status == AgentStatus.IDLE


class TestArtifacts:
    async def test_add_artifact_to_task(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        artifact = await agent_service.add_artifact(
            task_id=task.id,
            file_path="src/personal_jira/models/agent.py",
            content="class Agent: pass",
            artifact_type=ArtifactType.SOURCE,
        )
        assert artifact.id is not None
        assert artifact.file_path == "src/personal_jira/models/agent.py"
        assert artifact.artifact_type == ArtifactType.SOURCE

    async def test_add_test_artifact(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        artifact = await agent_service.add_artifact(
            task_id=task.id,
            file_path="tests/test_agent.py",
            content="def test_agent(): pass",
            artifact_type=ArtifactType.TEST,
        )
        assert artifact.artifact_type == ArtifactType.TEST

    async def test_list_artifacts_for_task(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.add_artifact(task_id=task.id, file_path="a.py", content="a", artifact_type=ArtifactType.SOURCE)
        await agent_service.add_artifact(task_id=task.id, file_path="b.py", content="b", artifact_type=ArtifactType.TEST)
        artifacts = await agent_service.get_artifacts(task.id)
        assert len(artifacts) == 2

    async def test_artifact_linked_to_issue(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        artifact = await agent_service.add_artifact(
            task_id=task.id,
            file_path="x.py",
            content="x",
            artifact_type=ArtifactType.SOURCE,
        )
        assert artifact.issue_id == sample_issue.id


class TestReviewLoop:
    async def test_submit_for_review(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        updated = await agent_service.submit_for_review(task.id, summary="Feature done")
        assert updated.result == TaskResult.IN_REVIEW

    async def test_approve_review(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="Done")
        updated = await agent_service.approve_review(task.id, feedback="LGTM")
        assert updated.result == TaskResult.APPROVED

    async def test_reject_review_allows_retry(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="Done")
        updated = await agent_service.reject_review(task.id, feedback="Fix tests")
        assert updated.result == TaskResult.CHANGES_REQUESTED

    async def test_reject_increments_review_count(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="v1")
        await agent_service.reject_review(task.id, feedback="Fix")
        await session.refresh(task)
        assert task.review_count == 1

    async def test_approve_sets_agent_idle(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="Done")
        await agent_service.approve_review(task.id, feedback="OK")
        await session.refresh(sample_agent)
        assert sample_agent.status == AgentStatus.IDLE


class TestTimeLimit:
    async def test_task_has_deadline(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        assert task.deadline is not None
        assert task.deadline > datetime.now(timezone.utc)

    async def test_check_expired_tasks(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        task.deadline = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()
        expired = await agent_service.get_expired_tasks()
        assert len(expired) == 1
        assert expired[0].id == task.id

    async def test_timeout_task_marks_failed(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        task.deadline = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()
        timed_out = await agent_service.timeout_expired_tasks()
        assert len(timed_out) == 1
        await session.refresh(task)
        assert task.result == TaskResult.TIMED_OUT

    async def test_timeout_releases_agent(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        task.deadline = datetime.now(timezone.utc) - timedelta(minutes=1)
        await session.commit()
        await agent_service.timeout_expired_tasks()
        await session.refresh(sample_agent)
        assert sample_agent.status == AgentStatus.IDLE


class TestMetrics:
    async def test_get_agent_metrics(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.add_work_log(task_id=task.id, summary="Work", llm_calls=3, tokens_used=500)
        await agent_service.submit_for_review(task.id, summary="Done")
        await agent_service.approve_review(task.id, feedback="OK")

        metrics = await agent_service.get_agent_metrics(sample_agent.id)
        assert metrics["total_tasks"] == 1
        assert metrics["successful_tasks"] == 1
        assert metrics["failed_tasks"] == 0
        assert metrics["total_llm_calls"] == 3
        assert metrics["total_tokens_used"] == 500

    async def test_metrics_with_failures(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.fail_task(task.id, error_message="Error")

        issue2 = Issue(title="Issue 2", issue_type=IssueType.TASK, status=IssueStatus.TODO, priority=IssuePriority.HIGH)
        session.add(issue2)
        await session.commit()
        await session.refresh(issue2)

        task2 = await agent_service.claim_task(sample_agent.id, issue2.id)
        await agent_service.submit_for_review(task2.id, summary="OK")
        await agent_service.approve_review(task2.id, feedback="OK")

        metrics = await agent_service.get_agent_metrics(sample_agent.id)
        assert metrics["total_tasks"] == 2
        assert metrics["successful_tasks"] == 1
        assert metrics["failed_tasks"] == 1

    async def test_metrics_success_rate(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="Done")
        await agent_service.approve_review(task.id, feedback="OK")

        metrics = await agent_service.get_agent_metrics(sample_agent.id)
        assert metrics["success_rate"] == 1.0

    async def test_metrics_average_review_rounds(self, agent_service: AgentService, sample_agent: Agent, sample_issue: Issue, session: AsyncSession):
        task = await agent_service.claim_task(sample_agent.id, sample_issue.id)
        await agent_service.submit_for_review(task.id, summary="v1")
        await agent_service.reject_review(task.id, feedback="Fix")
        await agent_service.submit_for_review(task.id, summary="v2")
        await agent_service.approve_review(task.id, feedback="OK")

        metrics = await agent_service.get_agent_metrics(sample_agent.id)
        assert metrics["avg_review_rounds"] == 1.0
