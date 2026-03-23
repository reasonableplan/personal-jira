import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.personal_jira.schemas.dashboard import (
    DashboardStats,
    StatusCount,
    PriorityCount,
    AssigneeCount,
)


class TestDashboardSchemas:
    def test_status_count(self) -> None:
        sc = StatusCount(status="Backlog", count=5)
        assert sc.status == "Backlog"
        assert sc.count == 5

    def test_priority_count(self) -> None:
        pc = PriorityCount(priority="High", count=3)
        assert pc.priority == "High"
        assert pc.count == 3

    def test_assignee_count(self) -> None:
        agent_id = uuid.uuid4()
        ac = AssigneeCount(assignee_id=agent_id, count=2)
        assert ac.assignee_id == agent_id
        assert ac.count == 2

    def test_assignee_count_unassigned(self) -> None:
        ac = AssigneeCount(assignee_id=None, count=7)
        assert ac.assignee_id is None

    def test_dashboard_stats(self) -> None:
        stats = DashboardStats(
            total=10,
            by_status=[StatusCount(status="Backlog", count=5), StatusCount(status="Done", count=5)],
            by_priority=[PriorityCount(priority="High", count=10)],
            by_assignee=[AssigneeCount(assignee_id=None, count=10)],
            done_count=5,
            completion_rate=50.0,
        )
        assert stats.total == 10
        assert stats.completion_rate == 50.0
        assert len(stats.by_status) == 2

    def test_completion_rate_zero_total(self) -> None:
        stats = DashboardStats(
            total=0,
            by_status=[],
            by_priority=[],
            by_assignee=[],
            done_count=0,
            completion_rate=0.0,
        )
        assert stats.completion_rate == 0.0


class TestDashboardService:
    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, mock_db: AsyncMock) -> None:
        from src.personal_jira.services.dashboard import DashboardService

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = DashboardService(mock_db)
        stats = await service.get_stats()

        assert stats.total == 0
        assert stats.done_count == 0
        assert stats.completion_rate == 0.0
        assert stats.by_status == []
        assert stats.by_priority == []
        assert stats.by_assignee == []

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self, mock_db: AsyncMock) -> None:
        from src.personal_jira.services.dashboard import DashboardService

        agent_id = uuid.uuid4()

        status_rows = [("Backlog", 3), ("Done", 2)]
        priority_rows = [("High", 4), ("Low", 1)]
        assignee_rows = [(agent_id, 3), (None, 2)]

        mock_results = [
            MagicMock(all=MagicMock(return_value=status_rows)),
            MagicMock(all=MagicMock(return_value=priority_rows)),
            MagicMock(all=MagicMock(return_value=assignee_rows)),
        ]
        mock_db.execute = AsyncMock(side_effect=mock_results)

        service = DashboardService(mock_db)
        stats = await service.get_stats()

        assert stats.total == 5
        assert stats.done_count == 2
        assert stats.completion_rate == pytest.approx(40.0)
        assert len(stats.by_status) == 2
        assert len(stats.by_priority) == 2
        assert len(stats.by_assignee) == 2

    @pytest.mark.asyncio
    async def test_get_stats_all_done(self, mock_db: AsyncMock) -> None:
        from src.personal_jira.services.dashboard import DashboardService

        status_rows = [("Done", 10)]
        priority_rows = [("Medium", 10)]
        assignee_rows = [(uuid.uuid4(), 10)]

        mock_results = [
            MagicMock(all=MagicMock(return_value=status_rows)),
            MagicMock(all=MagicMock(return_value=priority_rows)),
            MagicMock(all=MagicMock(return_value=assignee_rows)),
        ]
        mock_db.execute = AsyncMock(side_effect=mock_results)

        service = DashboardService(mock_db)
        stats = await service.get_stats()

        assert stats.total == 10
        assert stats.done_count == 10
        assert stats.completion_rate == pytest.approx(100.0)


class TestDashboardEndpoint:
    @pytest.fixture
    def mock_db(self) -> AsyncMock:
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, mock_db: AsyncMock) -> None:
        from src.personal_jira.api.v1.endpoints.dashboard import router
        from src.personal_jira.database import get_db

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        app.dependency_overrides[get_db] = lambda: mock_db

        status_rows = [("Backlog", 3), ("InProgress", 2), ("Done", 5)]
        priority_rows = [("High", 4), ("Medium", 3), ("Low", 3)]
        assignee_rows = [(uuid.uuid4(), 7), (None, 3)]

        mock_results = [
            MagicMock(all=MagicMock(return_value=status_rows)),
            MagicMock(all=MagicMock(return_value=priority_rows)),
            MagicMock(all=MagicMock(return_value=assignee_rows)),
        ]
        mock_db.execute = AsyncMock(side_effect=mock_results)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/dashboard/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10
        assert data["done_count"] == 5
        assert data["completion_rate"] == pytest.approx(50.0)
        assert len(data["by_status"]) == 3
        assert len(data["by_priority"]) == 3
        assert len(data["by_assignee"]) == 2

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_empty(self, mock_db: AsyncMock) -> None:
        from src.personal_jira.api.v1.endpoints.dashboard import router
        from src.personal_jira.database import get_db

        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        app.dependency_overrides[get_db] = lambda: mock_db

        mock_results = [
            MagicMock(all=MagicMock(return_value=[])),
            MagicMock(all=MagicMock(return_value=[])),
            MagicMock(all=MagicMock(return_value=[])),
        ]
        mock_db.execute = AsyncMock(side_effect=mock_results)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/dashboard/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["completion_rate"] == 0.0
