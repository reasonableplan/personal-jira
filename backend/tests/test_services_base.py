import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.base import Base
from app.services.base import GenericCRUDService
from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


class FakeModel(Base):
    __tablename__ = "fake_models"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100))


class FakeCreate(BaseModel):
    name: str


class FakeUpdate(BaseModel):
    name: str | None = None


class FakeService(GenericCRUDService[FakeModel, FakeCreate, FakeUpdate]):
    model = FakeModel


@pytest.fixture
def service() -> FakeService:
    return FakeService()


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


class TestGenericCRUDServiceInit:
    def test_subclass_has_model(self, service: FakeService) -> None:
        assert service.model is FakeModel

    def test_is_instance_of_generic(self, service: FakeService) -> None:
        assert isinstance(service, GenericCRUDService)


class TestGetById:
    @pytest.mark.anyio
    async def test_get_by_id_found(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        fake = FakeModel(id="abc", name="test")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = fake
        mock_session.execute.return_value = result_mock
        result = await service.get_by_id(mock_session, "abc")
        assert result is fake
        mock_session.execute.assert_awaited_once()

    @pytest.mark.anyio
    async def test_get_by_id_not_found(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        result = await service.get_by_id(mock_session, "nonexistent")
        assert result is None


class TestList:
    @pytest.mark.anyio
    async def test_list_default_pagination(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        items_mock = MagicMock()
        items_mock.scalars.return_value.all.return_value = []
        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        mock_session.execute.side_effect = [count_mock, items_mock]
        items, total = await service.list(mock_session)
        assert items == []
        assert total == 0

    @pytest.mark.anyio
    async def test_list_with_pagination(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        fake1 = FakeModel(id="1", name="a")
        fake2 = FakeModel(id="2", name="b")
        items_mock = MagicMock()
        items_mock.scalars.return_value.all.return_value = [fake1, fake2]
        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 5
        mock_session.execute.side_effect = [count_mock, items_mock]
        items, total = await service.list(mock_session, page=1, per_page=2)
        assert len(items) == 2
        assert total == 5


class TestCreate:
    @pytest.mark.anyio
    async def test_create(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        schema = FakeCreate(name="new")
        result = await service.create(mock_session, schema)
        assert isinstance(result, FakeModel)
        assert result.name == "new"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()


class TestUpdate:
    @pytest.mark.anyio
    async def test_update(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        existing = FakeModel(id="abc", name="old")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock
        schema = FakeUpdate(name="updated")
        result = await service.update(mock_session, "abc", schema)
        assert result is not None
        assert result.name == "updated"
        mock_session.flush.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    @pytest.mark.anyio
    async def test_update_not_found(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        schema = FakeUpdate(name="updated")
        result = await service.update(mock_session, "nonexistent", schema)
        assert result is None

    @pytest.mark.anyio
    async def test_update_partial(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        existing = FakeModel(id="abc", name="old")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock
        schema = FakeUpdate()
        result = await service.update(mock_session, "abc", schema)
        assert result is not None
        assert result.name == "old"


class TestDelete:
    @pytest.mark.anyio
    async def test_delete_found(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        existing = FakeModel(id="abc", name="old")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock
        result = await service.delete(mock_session, "abc")
        assert result is True
        mock_session.delete.assert_awaited_once_with(existing)
        mock_session.flush.assert_awaited_once()

    @pytest.mark.anyio
    async def test_delete_not_found(
        self, service: FakeService, mock_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock
        result = await service.delete(mock_session, "nonexistent")
        assert result is False
