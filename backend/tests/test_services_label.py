from unittest.mock import AsyncMock, MagicMock

import pytest
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.label import LabelService


@pytest.fixture
def service() -> LabelService:
    return LabelService()


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


class TestLabelServiceCreate:
    @pytest.mark.anyio
    async def test_create(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        body = LabelCreate(name="bug", color="#FF0000")
        result = await service.create(mock_session, body)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        assert result is not None


class TestLabelServiceGetByName:
    @pytest.mark.anyio
    async def test_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_label = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_label
        mock_session.execute.return_value = mock_result
        result = await service.get_by_name(mock_session, "bug")
        assert result is mock_label

    @pytest.mark.anyio
    async def test_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await service.get_by_name(mock_session, "nonexistent")
        assert result is None


class TestLabelServiceListAll:
    @pytest.mark.anyio
    async def test_list(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        labels = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = labels
        mock_session.execute.return_value = mock_result
        result = await service.list_all(mock_session)
        assert len(result) == 2


class TestLabelServiceUpdate:
    @pytest.mark.anyio
    async def test_update_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_label = MagicMock()
        mock_label.name = "bug"
        mock_label.color = "#FF0000"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_label
        mock_session.execute.return_value = mock_result
        body = LabelUpdate(name="bugfix")
        result = await service.update(mock_session, "l1", body)
        assert result is not None
        mock_session.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_update_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        body = LabelUpdate(name="bugfix")
        result = await service.update(mock_session, "nonexistent", body)
        assert result is None


class TestLabelServiceDelete:
    @pytest.mark.anyio
    async def test_delete_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_label = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_label
        mock_session.execute.return_value = mock_result
        result = await service.delete(mock_session, "l1")
        assert result is True
        mock_session.delete.assert_awaited_once()

    @pytest.mark.anyio
    async def test_delete_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await service.delete(mock_session, "nonexistent")
        assert result is False


class TestLabelServiceAttach:
    @pytest.mark.anyio
    async def test_attach_labels(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        result = await service.attach_labels_to_task(
            mock_session, "t1", ["l1", "l2"]
        )
        assert isinstance(result, list)


class TestLabelServiceDetach:
    @pytest.mark.anyio
    async def test_detach_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_session.execute.return_value = mock_result
        result = await service.detach_label_from_task(
            mock_session, "t1", "l1"
        )
        assert result is True

    @pytest.mark.anyio
    async def test_detach_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await service.detach_label_from_task(
            mock_session, "t1", "l1"
        )
        assert result is False
