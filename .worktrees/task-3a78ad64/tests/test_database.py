from app.database import get_async_session, async_engine


def test_engine_is_configured() -> None:
    assert async_engine is not None
    assert "asyncpg" in str(async_engine.url.drivername) or "sqlite" in str(
        async_engine.url.drivername
    )


def test_get_async_session_is_async_generator() -> None:
    gen = get_async_session()
    assert hasattr(gen, "__anext__")
