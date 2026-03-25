from unittest.mock import AsyncMock, MagicMock

import pytest
from app.schemas.label import LabelCreate, LabelUpdate
from app.services.label import LabelService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def service() -> LabelService:
    return LabelService()


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


class TestLabelServiceCreate:
    @pytest.mark.anyio
    async def test_create_label(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        schema = LabelCreate(name="bug", color="#FF0000")
        result = await service.create(mock_session, schema)
        assert result.name == "bug"
        assert result.color == "#FF0000"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()


class TestLabelServiceGetByName:
    @pytest.mark.anyio
    async def test_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        from app.models.issue import Label

        fake = Label(id="abc", name="bug", color="#FF0000")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = fake
        mock_session.execute.return_value = result_mock
        result = await service.get_by_name(mock_session, "bug")
        assert result is fake

    @pytest.mark.anyio
    async def test_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        result = await service.get_by_name(mock_session, "nonexistent")
        assert result is None


class TestLabelServiceListAll:
    @pytest.mark.anyio
    async def test_list_all(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        from app.models.issue import Label

        fake1 = Label(id="1", name="bug", color="#FF0000")
        fake2 = Label(id="2", name="feature", color="#00FF00")
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [fake1, fake2]
        mock_session.execute.return_value = result_mock
        result = await service.list_all(mock_session)
        assert len(result) == 2
        assert result[0].name == "bug"

    @pytest.mark.anyio
    async def test_list_all_empty(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = result_mock
        result = await service.list_all(mock_session)
        assert result == []


class TestLabelServiceUpdate:
    @pytest.mark.anyio
    async def test_update(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        from app.models.issue import Label

        existing = Label(id="abc", name="bug", color="#FF0000")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock
        schema = LabelUpdate(color="#00FF00")
        result = await service.update(mock_session, "abc", schema)
        assert result is not None
        assert result.color == "#00FF00"

    @pytest.mark.anyio
    async def test_update_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        schema = LabelUpdate(name="new")
        result = await service.update(mock_session, "nonexistent", schema)
        assert result is None


class TestLabelServiceDelete:
    @pytest.mark.anyio
    async def test_delete_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        from app.models.issue import Label

        existing = Label(id="abc", name="bug", color="#FF0000")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock
        result = await service.delete(mock_session, "abc")
        assert result is True
        mock_session.delete.assert_awaited_once_with(existing)

    @pytest.mark.anyio
    async def test_delete_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        result = await service.delete(mock_session, "nonexistent")
        assert result is False


class TestAttachLabelsToTask:
    @pytest.mark.anyio
    async def test_attach_new_labels(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        existing_result = MagicMock()
        existing_result.fetchall.return_value = []
        final_result = MagicMock()
        final_result.fetchall.return_value = [("label1",), ("label2",)]
        mock_session.execute.side_effect = [
            existing_result,
            MagicMock(),  # insert label1
            MagicMock(),  # insert label2
            final_result,
        ]
        result = await service.attach_labels_to_task(
            mock_session, "task1", ["label1", "label2"]
        )
        assert result == ["label1", "label2"]
        mock_session.flush.assert_awaited_once()

    @pytest.mark.anyio
    async def test_attach_skips_existing(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        existing_result = MagicMock()
        existing_result.fetchall.return_value = [("label1",)]
        final_result = MagicMock()
        final_result.fetchall.return_value = [("label1",), ("label2",)]
        mock_session.execute.side_effect = [
            existing_result,
            MagicMock(),  # insert label2 only
            final_result,
        ]
        result = await service.attach_labels_to_task(
            mock_session, "task1", ["label1", "label2"]
        )
        assert result == ["label1", "label2"]


class TestDetachLabelFromTask:
    @pytest.mark.anyio
    async def test_detach_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.rowcount = 1
        mock_session.execute.return_value = result_mock
        result = await service.detach_label_from_task(
            mock_session, "task1", "label1"
        )
        assert result is True
        mock_session.flush.assert_awaited_once()

    @pytest.mark.anyio
    async def test_detach_not_found(
        self, service: LabelService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.rowcount = 0
        mock_session.execute.return_value = result_mock
        result = await service.detach_label_from_task(
            mock_session, "task1", "label1"
        )
        assert result is False
