from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.database import get_db, get_engine, get_session_factory


def test_get_engine():
    engine = get_engine("sqlite+aiosqlite:///")
    assert isinstance(engine, AsyncEngine)
    assert str(engine.url) == "sqlite+aiosqlite:///"


def test_get_session_factory():
    engine = get_engine("sqlite+aiosqlite:///")
    factory = get_session_factory(engine)
    assert factory is not None


async def test_get_db():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_factory = AsyncMock(return_value=mock_session)
    mock_factory.__aenter__ = AsyncMock(return_value=mock_session)
    mock_factory.__aexit__ = AsyncMock(return_value=None)

    with patch("app.database._session_factory", mock_factory):
        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session
