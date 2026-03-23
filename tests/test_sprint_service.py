import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from personal_jira.models.sprint import Sprint, SprintStatus
from personal_jira.schemas.sprint import SprintCreate, SprintUpdate
from personal_jira.services.sprint import SprintService


@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def service() -> SprintService:
    return SprintService()


class TestSprintServiceCreate:
    @pytest.mark.asyncio
    async def test_create_sprint(self, service: SprintService, mock_db: AsyncMock) -> None:
        data = SprintCreate(
            name="Sprint 1",
            goal="Complete MVP",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        result = await service.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()
        assert isinstance(result, Sprint)
        assert result.name == "Sprint 1"
        assert result.status == SprintStatus.PLANNING


class TestSprintServiceGet:
    @pytest.mark.asyncio
    async def test_get_sprint_found(self, service: SprintService, mock_db: AsyncMock) -> None:
        sprint_id = uuid.uuid4()
        mock_sprint = Sprint(
            id=sprint_id,
            name="Sprint 1",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_sprint
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id(mock_db, sprint_id)
        assert result is not None
        assert result.id == sprint_id

    @pytest.mark.asyncio
    async def test_get_sprint_not_found(self, service: SprintService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.get_by_id(mock_db, uuid.uuid4())
        assert result is None


class TestSprintServiceUpdate:
    @pytest.mark.asyncio
    async def test_update_sprint(self, service: SprintService, mock_db: AsyncMock) -> None:
        sprint_id = uuid.uuid4()
        existing = Sprint(
            id=sprint_id,
            name="Sprint 1",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        update_data = SprintUpdate(name="Updated Sprint", status="active")
        result = await service.update(mock_db, sprint_id, update_data)

        assert result is not None
        assert result.name == "Updated Sprint"
        assert result.status == SprintStatus.ACTIVE
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_sprint_not_found(self, service: SprintService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        update_data = SprintUpdate(name="Updated")
        result = await service.update(mock_db, uuid.uuid4(), update_data)
        assert result is None


class TestSprintServiceList:
    @pytest.mark.asyncio
    async def test_list_sprints(self, service: SprintService, mock_db: AsyncMock) -> None:
        sprints = [
            Sprint(name="Sprint 1", start_date=date(2026, 3, 1), end_date=date(2026, 3, 14)),
            Sprint(name="Sprint 2", start_date=date(2026, 3, 15), end_date=date(2026, 3, 28)),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sprints
        mock_db.execute.return_value = mock_result

        result = await service.list_all(mock_db)
        assert len(result) == 2


class TestSprintServiceDelete:
    @pytest.mark.asyncio
    async def test_delete_sprint(self, service: SprintService, mock_db: AsyncMock) -> None:
        sprint_id = uuid.uuid4()
        existing = Sprint(
            id=sprint_id,
            name="Sprint 1",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = mock_result

        result = await service.delete(mock_db, sprint_id)
        assert result is True
        mock_db.delete.assert_awaited_once_with(existing)
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_sprint_not_found(self, service: SprintService, mock_db: AsyncMock) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await service.delete(mock_db, uuid.uuid4())
        assert result is False
