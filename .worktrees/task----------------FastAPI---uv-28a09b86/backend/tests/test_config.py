import pytest
from app.config import Settings


class TestSettings:
    def test_default_database_url(self) -> None:
        s = Settings()
        assert "postgresql+asyncpg://" in s.database_url

    def test_default_cors_origins(self) -> None:
        s = Settings()
        assert isinstance(s.cors_origins, list)
        assert len(s.cors_origins) > 0

    def test_custom_database_url(self) -> None:
        s = Settings(database_url="postgresql+asyncpg://u:p@host:5432/db")
        assert s.database_url == "postgresql+asyncpg://u:p@host:5432/db"

    def test_debug_default_false(self) -> None:
        s = Settings()
        assert s.debug is False
