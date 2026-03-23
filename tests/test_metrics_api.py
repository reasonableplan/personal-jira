import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from personal_jira.app import create_app
from personal_jira.schemas.metrics import AgentMetrics, IssueMetrics, MetricsSummary


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestGetAgentMetricsEndpoint:
    @pytest.mark.asyncio
    async def test_get_agent_metrics_success(self, client: AsyncClient) -> None:
        metrics = AgentMetrics(
            agent_id="agent-backend",
            total_tasks=10,
            completed_tasks=8,
            failed_tasks=1,
            review_pass_rate=0.85,
            rework_count=2,
            avg_completion_seconds=3600.0,
            total_work_seconds=28800.0,
        )
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_svc.get_agent_metrics.return_value = metrics
            mock_get_svc.return_value = mock_svc

            response = await client.get("/api/v1/metrics/agents/agent-backend")

        assert response.status_code == 200
        data = response.json()
        assert data["agent"]["agent_id"] == "agent-backend"
        assert data["agent"]["review_pass_rate"] == 0.85
        assert data["agent"]["rework_count"] == 2

    @pytest.mark.asyncio
    async def test_get_agent_metrics_empty(self, client: AsyncClient) -> None:
        metrics = AgentMetrics(
            agent_id="unknown-agent",
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            review_pass_rate=0.0,
            rework_count=0,
            avg_completion_seconds=0.0,
            total_work_seconds=0.0,
        )
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_svc.get_agent_metrics.return_value = metrics
            mock_get_svc.return_value = mock_svc

            response = await client.get("/api/v1/metrics/agents/unknown-agent")

        assert response.status_code == 200
        assert response.json()["agent"]["total_tasks"] == 0


class TestGetIssueMetricsEndpoint:
    @pytest.mark.asyncio
    async def test_get_issue_metrics_success(self, client: AsyncClient) -> None:
        issue_id = str(uuid4())
        metrics = IssueMetrics(
            issue_id=issue_id,
            title="Test",
            status="Done",
            assigned_agent="agent-backend",
            review_attempts=2,
            rework_count=1,
            total_work_seconds=7200.0,
            elapsed_seconds=14400.0,
        )
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_svc.get_issue_metrics.return_value = metrics
            mock_get_svc.return_value = mock_svc

            response = await client.get(f"/api/v1/metrics/issues/{issue_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["issue"]["issue_id"] == issue_id
        assert data["issue"]["rework_count"] == 1

    @pytest.mark.asyncio
    async def test_get_issue_metrics_not_found(self, client: AsyncClient) -> None:
        issue_id = str(uuid4())
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_svc.get_issue_metrics.return_value = None
            mock_get_svc.return_value = mock_svc

            response = await client.get(f"/api/v1/metrics/issues/{issue_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_issue_metrics_invalid_uuid(self, client: AsyncClient) -> None:
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_get_svc.return_value = mock_svc

            response = await client.get("/api/v1/metrics/issues/not-a-uuid")

        assert response.status_code == 422


class TestGetSummaryEndpoint:
    @pytest.mark.asyncio
    async def test_get_summary_success(self, client: AsyncClient) -> None:
        summary = MetricsSummary(
            total_issues=50,
            completed_issues=40,
            in_progress_issues=8,
            blocked_issues=2,
            overall_review_pass_rate=0.9,
            overall_avg_completion_seconds=5400.0,
            total_rework_count=12,
            active_agents=3,
        )
        with patch(
            "personal_jira.api.v1.endpoints.metrics.get_metrics_service"
        ) as mock_get_svc:
            mock_svc = AsyncMock()
            mock_svc.get_summary.return_value = summary
            mock_get_svc.return_value = mock_svc

            response = await client.get("/api/v1/metrics/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_issues"] == 50
        assert data["summary"]["overall_review_pass_rate"] == 0.9
        assert data["summary"]["active_agents"] == 3
