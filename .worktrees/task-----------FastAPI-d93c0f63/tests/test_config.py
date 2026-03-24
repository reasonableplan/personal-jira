from app.config import Settings


def test_default_settings():
    settings = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb")
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/testdb"
    assert settings.TESTING is False
    assert settings.APP_NAME == "fastapi-app"
    assert settings.DEBUG is False


def test_testing_flag():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb",
        TESTING=True,
    )
    assert settings.TESTING is True


def test_debug_flag():
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb",
        DEBUG=True,
    )
    assert settings.DEBUG is True
