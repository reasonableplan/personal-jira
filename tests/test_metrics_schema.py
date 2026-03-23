import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from personal_jira.schemas.metrics import (
    AgentMetrics,
    IssueMetrics,
    AgentMetricsResponse,
    IssueMetricsResponse,
    MetricsSummary,
    MetricsSummaryResponse,
    TimeRange,
)


class TestTimeRange:
    def test_valid_time_range(self) -> None:
        tr = TimeRange(
            start=datetime(2026, 1, 1),
            end=datetime(2026, 3, 1),
        )
        assert tr.start < tr.end

    def test_end_before_start_raises(self) -> None:
        with pytest.raises(ValidationError):
            TimeRange(
                start=datetime(2026, 3, 1),
                end=datetime(2026, 1, 1),
            )


class TestAgentMetrics:
    def test_create_agent_metrics(self) -> None:
        m = AgentMetrics(
            agent_id="agent-backend",
            total_tasks=20,
            completed_tasks=18,
            failed_tasks=2,
            review_pass_rate=0.85,
            rework_count=3,
            avg_completion_seconds=3600.0,
            total_work_seconds=64800.0,
        )
        assert m.agent_id == "agent-backend"
        assert m.review_pass_rate == 0.85
        assert m.rework_count == 3

    def test_review_pass_rate_bounds(self) -> None:
        with pytest.raises(ValidationError):
            AgentMetrics(
                agent_id="a",
                total_tasks=1,
                completed_tasks=1,
                failed_tasks=0,
                review_pass_rate=1.5,
                rework_count=0,
                avg_completion_seconds=0.0,
                total_work_seconds=0.0,
            )

    def test_negative_rework_count_raises(self) -> None:
        with pytest.raises(ValidationError):
            AgentMetrics(
                agent_id="a",
                total_tasks=1,
                completed_tasks=1,
                failed_tasks=0,
                review_pass_rate=0.5,
                rework_count=-1,
                avg_completion_seconds=0.0,
                total_work_seconds=0.0,
            )


class TestIssueMetrics:
    def test_create_issue_metrics(self) -> None:
        m = IssueMetrics(
            issue_id="550e8400-e29b-41d4-a716-446655440000",
            title="Test issue",
            status="Done",
            assigned_agent="agent-backend",
            review_attempts=3,
            rework_count=1,
            total_work_seconds=7200.0,
            elapsed_seconds=14400.0,
        )
        assert m.review_attempts == 3
        assert m.rework_count == 1


class TestMetricsSummary:
    def test_create_summary(self) -> None:
        s = MetricsSummary(
            total_issues=50,
            completed_issues=40,
            in_progress_issues=8,
            blocked_issues=2,
            overall_review_pass_rate=0.9,
            overall_avg_completion_seconds=5400.0,
            total_rework_count=12,
            active_agents=3,
        )
        assert s.total_issues == 50
        assert s.overall_review_pass_rate == 0.9


class TestAgentMetricsResponse:
    def test_response_structure(self) -> None:
        r = AgentMetricsResponse(
            agent=AgentMetrics(
                agent_id="agent-backend",
                total_tasks=10,
                completed_tasks=8,
                failed_tasks=2,
                review_pass_rate=0.8,
                rework_count=2,
                avg_completion_seconds=3600.0,
                total_work_seconds=28800.0,
            ),
        )
        assert r.agent.agent_id == "agent-backend"


class TestIssueMetricsResponse:
    def test_response_structure(self) -> None:
        r = IssueMetricsResponse(
            issue=IssueMetrics(
                issue_id="550e8400-e29b-41d4-a716-446655440000",
                title="Test",
                status="Done",
                assigned_agent=None,
                review_attempts=1,
                rework_count=0,
                total_work_seconds=3600.0,
                elapsed_seconds=7200.0,
            ),
        )
        assert r.issue.issue_id == "550e8400-e29b-41d4-a716-446655440000"


class TestMetricsSummaryResponse:
    def test_response_structure(self) -> None:
        r = MetricsSummaryResponse(
            summary=MetricsSummary(
                total_issues=10,
                completed_issues=5,
                in_progress_issues=3,
                blocked_issues=2,
                overall_review_pass_rate=0.75,
                overall_avg_completion_seconds=4000.0,
                total_rework_count=4,
                active_agents=2,
            ),
        )
        assert r.summary.total_issues == 10
