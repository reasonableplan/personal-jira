import os

import pytest

from app.config import Settings


class TestSettings:
    def test_default_values(self) -> None:
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb",
        )
        assert settings.APP_NAME == "fastapi-app"
        assert settings.DEBUG is False
        assert settings.API_V1_PREFIX == "/api/v1"
        assert "postgresql+asyncpg" in settings.DATABASE_URL

    def test_database_url_required(self) -> None:
        env_backup = os.environ.get("DATABASE_URL")
        os.environ.pop("DATABASE_URL", None)
        with pytest.raises(Exception):
            Settings()  # type: ignore[call-arg]
        if env_backup is not None:
            os.environ["DATABASE_URL"] = env_backup

    def test_custom_values(self) -> None:
        settings = Settings(
            APP_NAME="custom-app",
            DEBUG=True,
            API_V1_PREFIX="/api/v2",
            DATABASE_URL="postgresql+asyncpg://u:p@db:5432/custom",
        )
        assert settings.APP_NAME == "custom-app"
        assert settings.DEBUG is True
        assert settings.API_V1_PREFIX == "/api/v2"
