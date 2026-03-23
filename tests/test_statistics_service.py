import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from personal_jira.schemas.statistics import (
    AgentStatistics,
    DashboardStatistics,
    StatusBreakdown,
)
from personal_jira.services.statistics import StatisticsService


@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def service() -> StatisticsService:
    return StatisticsService()


class TestDashboardStatistics:
    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, service: StatisticsService, mock_db: AsyncMock) -> None:
        mock_total = MagicMock()
        mock_total.scalar_one.return_value = 25

        mock_status = MagicMock()
        mock_status.all.return_value = [
            ("backlog", 5),
            ("ready", 4),
            ("in_progress", 6),
            ("in_review", 3),
            ("done", 7),
        ]

        mock_avg = MagicMock()
        mock_avg.scalar_one.return_value = 3600.0

        mock_review = MagicMock()
        mock_review.scalar_one.return_value = 0.85

        mock_db.execute.side_effect = [mock_total, mock_status, mock_avg, mock_review]

        result = await service.get_dashboard(mock_db)

        assert isinstance(result, DashboardStatistics)
        assert result.total_issues == 25
        assert result.avg_completion_time_seconds == 3600.0
        assert result.review_pass_rate == 0.85
        assert len(result.status_breakdown) == 5

    @pytest.mark.asyncio
    async def test_get_dashboard_empty(self, service: StatisticsService, mock_db: AsyncMock) -> None:
        mock_total = MagicMock()
        mock_total.scalar_one.return_value = 0

        mock_status = MagicMock()
        mock_status.all.return_value = []

        mock_avg = MagicMock()
        mock_avg.scalar_one.return_value = None

        mock_review = MagicMock()
        mock_review.scalar_one.return_value = None

        mock_db.execute.side_effect = [mock_total, mock_status, mock_avg, mock_review]

        result = await service.get_dashboard(mock_db)

        assert result.total_issues == 0
        assert result.avg_completion_time_seconds is None
        assert result.review_pass_rate is None
        assert result.status_breakdown == []


class TestAgentStatistics:
    @pytest.mark.asyncio
    async def test_get_agent_stats(self, service: StatisticsService, mock_db: AsyncMock) -> None:
        agent_id = "agent-backend"

        mock_total = MagicMock()
        mock_total.scalar_one.return_value = 10

        mock_completed = MagicMock()
        mock_completed.scalar_one.return_value = 7

        mock_avg = MagicMock()
        mock_avg.scalar_one.return_value = 1800.0

        mock_rework = MagicMock()
        mock_rework.scalar_one.return_value = 2

        mock_review_pass = MagicMock()
        mock_review_pass.scalar_one.return_value = 0.9

        mock_db.execute.side_effect = [
            mock_total, mock_completed, mock_avg, mock_rework, mock_review_pass,
        ]

        result = await service.get_agent_stats(mock_db, agent_id)

        assert isinstance(result, AgentStatistics)
        assert result.agent_id == agent_id
        assert result.total_assigned == 10
        assert result.total_completed == 7
        assert result.avg_completion_time_seconds == 1800.0
        assert result.rework_count == 2
        assert result.review_pass_rate == 0.9

    @pytest.mark.asyncio
    async def test_get_agent_stats_no_tasks(self, service: StatisticsService, mock_db: AsyncMock) -> None:
        agent_id = "agent-new"

        mock_total = MagicMock()
        mock_total.scalar_one.return_value = 0

        mock_completed = MagicMock()
        mock_completed.scalar_one.return_value = 0

        mock_avg = MagicMock()
        mock_avg.scalar_one.return_value = None

        mock_rework = MagicMock()
        mock_rework.scalar_one.return_value = 0

        mock_review_pass = MagicMock()
        mock_review_pass.scalar_one.return_value = None

        mock_db.execute.side_effect = [
            mock_total, mock_completed, mock_avg, mock_rework, mock_review_pass,
        ]

        result = await service.get_agent_stats(mock_db, agent_id)

        assert result.total_assigned == 0
        assert result.total_completed == 0
        assert result.avg_completion_time_seconds is None
        assert result.review_pass_rate is None
