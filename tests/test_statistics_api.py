from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from personal_jira.app import create_app
from personal_jira.schemas.statistics import (
    AgentStatistics,
    DashboardStatistics,
    StatusBreakdown,
)

app = create_app()


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
async def client(mock_db):
    async def override_get_db():
        yield mock_db

    from personal_jira.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


class TestDashboardEndpoint:
    @pytest.mark.asyncio
    async def test_get_dashboard_200(self, client: AsyncClient) -> None:
        with patch(
            "personal_jira.api.statistics.statistics_service.get_dashboard",
            new_callable=AsyncMock,
        ) as mock_dash:
            mock_dash.return_value = DashboardStatistics(
                total_issues=25,
                status_breakdown=[
                    StatusBreakdown(status="done", count=10),
                    StatusBreakdown(status="in_progress", count=15),
                ],
                avg_completion_time_seconds=3600.0,
                review_pass_rate=0.85,
            )
            resp = await client.get("/api/v1/statistics/dashboard")

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_issues"] == 25
        assert len(data["status_breakdown"]) == 2
        assert data["avg_completion_time_seconds"] == 3600.0
        assert data["review_pass_rate"] == 0.85


class TestAgentStatsEndpoint:
    @pytest.mark.asyncio
    async def test_get_agent_stats_200(self, client: AsyncClient) -> None:
        with patch(
            "personal_jira.api.statistics.statistics_service.get_agent_stats",
            new_callable=AsyncMock,
        ) as mock_agent:
            mock_agent.return_value = AgentStatistics(
                agent_id="agent-backend",
                total_assigned=10,
                total_completed=7,
                avg_completion_time_seconds=1800.0,
                rework_count=2,
                review_pass_rate=0.9,
            )
            resp = await client.get("/api/v1/statistics/agents/agent-backend")

        assert resp.status_code == 200
        data = resp.json()
        assert data["agent_id"] == "agent-backend"
        assert data["total_assigned"] == 10
        assert data["total_completed"] == 7
