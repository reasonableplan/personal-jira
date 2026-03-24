import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_async_session(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_base_declarative():
    from app.database import Base

    assert hasattr(Base, "metadata")


def test_naming_convention():
    from app.database import Base

    nc = Base.metadata.naming_convention
    assert "ix" in nc
    assert "uq" in nc
    assert "ck" in nc
    assert "fk" in nc
    assert "pk" in nc


@pytest.mark.asyncio
async def test_get_db_yields_session():
    from app.database import get_db

    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass
