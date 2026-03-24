from app.core.config import Settings, get_settings


def test_settings_default_values() -> None:
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb",
    )
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/testdb"
    assert settings.APP_NAME == "fastapi-app"
    assert settings.DEBUG is False


def test_settings_custom_values() -> None:
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://u:p@host:5432/db",
        APP_NAME="custom-app",
        DEBUG=True,
    )
    assert settings.APP_NAME == "custom-app"
    assert settings.DEBUG is True


def test_get_settings_returns_settings_instance() -> None:
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_settings_is_cached() -> None:
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
