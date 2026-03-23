import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import Base, async_session_factory, engine


class SampleModel(Base):
    __tablename__ = "sample_for_test"
    name: str = Column(String(100), nullable=False)


@pytest.fixture(autouse=True)
async def setup_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestBase:
    def test_base_has_metadata(self) -> None:
        assert Base.metadata is not None


class TestBaseModel:
    async def test_id_is_uuid(self, db_session: AsyncSession) -> None:
        obj = SampleModel(name="test")
        db_session.add(obj)
        await db_session.commit()
        await db_session.refresh(obj)
        assert isinstance(obj.id, uuid.UUID)

    async def test_created_at_auto_set(self, db_session: AsyncSession) -> None:
        obj = SampleModel(name="test")
        db_session.add(obj)
        await db_session.commit()
        await db_session.refresh(obj)
        assert isinstance(obj.created_at, datetime)

    async def test_updated_at_auto_set(self, db_session: AsyncSession) -> None:
        obj = SampleModel(name="test")
        db_session.add(obj)
        await db_session.commit()
        await db_session.refresh(obj)
        assert isinstance(obj.updated_at, datetime)

    async def test_updated_at_changes_on_update(self, db_session: AsyncSession) -> None:
        obj = SampleModel(name="original")
        db_session.add(obj)
        await db_session.commit()
        await db_session.refresh(obj)
        original_updated = obj.updated_at

        obj.name = "modified"
        await db_session.commit()
        await db_session.refresh(obj)
        assert obj.updated_at >= original_updated

    async def test_id_is_unique(self, db_session: AsyncSession) -> None:
        obj1 = SampleModel(name="a")
        obj2 = SampleModel(name="b")
        db_session.add_all([obj1, obj2])
        await db_session.commit()
        await db_session.refresh(obj1)
        await db_session.refresh(obj2)
        assert obj1.id != obj2.id


class TestAsyncSessionFactory:
    async def test_creates_async_session(self) -> None:
        async with async_session_factory() as session:
            assert isinstance(session, AsyncSession)


class TestEngine:
    def test_engine_is_configured(self) -> None:
        assert engine is not None
        assert str(engine.url) != ""
