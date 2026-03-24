from app.core.config import Settings


def test_settings_default_values() -> None:
    settings = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test")
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/test"
    assert settings.APP_NAME == "app"
    assert settings.DEBUG is False


def test_settings_custom_values() -> None:
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/custom",
        APP_NAME="custom-app",
        DEBUG=True,
    )
    assert settings.APP_NAME == "custom-app"
    assert settings.DEBUG is True


def test_settings_singleton() -> None:
    from app.core.config import get_settings

    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
