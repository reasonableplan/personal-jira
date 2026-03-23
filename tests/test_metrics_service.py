import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from personal_jira.services.metrics_service import MetricsService
from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.models.work_log import WorkLog


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_db: AsyncMock) -> MetricsService:
    return MetricsService(mock_db)


class TestGetAgentMetrics:
    @pytest.mark.asyncio
    async def test_agent_with_no_tasks(self, service: MetricsService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await service.get_agent_metrics("agent-backend")

        assert result.agent_id == "agent-backend"
        assert result.total_tasks == 0
        assert result.completed_tasks == 0
        assert result.failed_tasks == 0
        assert result.review_pass_rate == 0.0
        assert result.rework_count == 0
        assert result.avg_completion_seconds == 0.0
        assert result.total_work_seconds == 0.0

    @pytest.mark.asyncio
    async def test_agent_with_completed_tasks(self, service: MetricsService, mock_db: AsyncMock) -> None:
        now = datetime.now(timezone.utc)
        issues = [
            _make_issue(status=IssueStatus.DONE, created_at=now - timedelta(hours=2), updated_at=now, review_count=1, rework_count=0),
            _make_issue(status=IssueStatus.DONE, created_at=now - timedelta(hours=4), updated_at=now - timedelta(hours=1), review_count=2, rework_count=1),
            _make_issue(status=IssueStatus.IN_PROGRESS, created_at=now - timedelta(hours=1), updated_at=now, review_count=0, rework_count=0),
        ]

        mock_result_issues = MagicMock()
        mock_result_issues.scalars.return_value.all.return_value = issues

        mock_result_worklogs = MagicMock()
        mock_result_worklogs.scalars.return_value.all.return_value = [
            _make_worklog(seconds=3600),
            _make_worklog(seconds=7200),
        ]

        mock_db.execute.side_effect = [mock_result_issues, mock_result_worklogs]

        result = await service.get_agent_metrics("agent-backend")

        assert result.total_tasks == 3
        assert result.completed_tasks == 2
        assert result.failed_tasks == 0
        assert result.rework_count == 1
        assert result.total_work_seconds == 10800.0

    @pytest.mark.asyncio
    async def test_agent_review_pass_rate(self, service: MetricsService, mock_db: AsyncMock) -> None:
        now = datetime.now(timezone.utc)
        issues = [
            _make_issue(status=IssueStatus.DONE, review_count=1, rework_count=0),
            _make_issue(status=IssueStatus.DONE, review_count=3, rework_count=2),
            _make_issue(status=IssueStatus.DONE, review_count=2, rework_count=1),
        ]

        mock_result_issues = MagicMock()
        mock_result_issues.scalars.return_value.all.return_value = issues
        mock_result_worklogs = MagicMock()
        mock_result_worklogs.scalars.return_value.all.return_value = []
        mock_db.execute.side_effect = [mock_result_issues, mock_result_worklogs]

        result = await service.get_agent_metrics("agent-backend")

        # 3 done issues, total review_count=6, rework=3 -> pass_rate = (6-3)/6 = 0.5
        assert result.review_pass_rate == 0.5


class TestGetIssueMetrics:
    @pytest.mark.asyncio
    async def test_issue_not_found(self, service: MetricsService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.get_issue_metrics(str(uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_issue_with_worklogs(self, service: MetricsService, mock_db: AsyncMock) -> None:
        now = datetime.now(timezone.utc)
        issue = _make_issue(
            status=IssueStatus.DONE,
            created_at=now - timedelta(hours=5),
            updated_at=now,
            review_count=2,
            rework_count=1,
        )

        mock_result_issue = MagicMock()
        mock_result_issue.scalar_one_or_none.return_value = issue

        mock_result_worklogs = MagicMock()
        mock_result_worklogs.scalars.return_value.all.return_value = [
            _make_worklog(seconds=1800),
            _make_worklog(seconds=3600),
        ]

        mock_db.execute.side_effect = [mock_result_issue, mock_result_worklogs]

        result = await service.get_issue_metrics(str(issue.id))

        assert result is not None
        assert result.review_attempts == 2
        assert result.rework_count == 1
        assert result.total_work_seconds == 5400.0
        assert result.elapsed_seconds == 18000.0


class TestGetSummary:
    @pytest.mark.asyncio
    async def test_empty_project(self, service: MetricsService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await service.get_summary()

        assert result.total_issues == 0
        assert result.completed_issues == 0
        assert result.in_progress_issues == 0
        assert result.blocked_issues == 0
        assert result.overall_review_pass_rate == 0.0
        assert result.active_agents == 0

    @pytest.mark.asyncio
    async def test_summary_with_mixed_issues(self, service: MetricsService, mock_db: AsyncMock) -> None:
        now = datetime.now(timezone.utc)
        issues = [
            _make_issue(status=IssueStatus.DONE, assigned_to="agent-a", review_count=1, rework_count=0, created_at=now - timedelta(hours=2), updated_at=now),
            _make_issue(status=IssueStatus.DONE, assigned_to="agent-b", review_count=2, rework_count=1, created_at=now - timedelta(hours=3), updated_at=now),
            _make_issue(status=IssueStatus.IN_PROGRESS, assigned_to="agent-a", review_count=0, rework_count=0),
            _make_issue(status=IssueStatus.BLOCKED, assigned_to=None, review_count=0, rework_count=0),
            _make_issue(status=IssueStatus.BACKLOG, assigned_to=None, review_count=0, rework_count=0),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = issues
        mock_db.execute.return_value = mock_result

        result = await service.get_summary()

        assert result.total_issues == 5
        assert result.completed_issues == 2
        assert result.in_progress_issues == 1
        assert result.blocked_issues == 1
        assert result.total_rework_count == 1
        assert result.active_agents == 2
        # review_pass_rate: total_reviews=3, reworks=1 -> (3-1)/3 = 0.6667
        assert round(result.overall_review_pass_rate, 4) == 0.6667
        assert result.overall_avg_completion_seconds > 0


def _make_issue(
    status: IssueStatus = IssueStatus.BACKLOG,
    assigned_to: str | None = "agent-backend",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    review_count: int = 0,
    rework_count: int = 0,
) -> MagicMock:
    now = datetime.now(timezone.utc)
    issue = MagicMock(spec=Issue)
    issue.id = uuid4()
    issue.title = "Test issue"
    issue.status = status
    issue.assigned_to = assigned_to
    issue.created_at = created_at or now
    issue.updated_at = updated_at or now
    issue.review_count = review_count
    issue.rework_count = rework_count
    return issue


def _make_worklog(seconds: float = 3600.0) -> MagicMock:
    wl = MagicMock(spec=WorkLog)
    wl.duration_seconds = seconds
    return wl
