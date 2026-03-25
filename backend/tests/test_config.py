from app.config import Settings, settings


class TestSettings:
    def test_default_database_url(self) -> None:
        s = Settings()
        assert "postgresql+asyncpg://" in s.database_url

    def test_default_cors_origins(self) -> None:
        s = Settings()
        assert "http://localhost:5173" in s.cors_origins

    def test_default_debug(self) -> None:
        s = Settings()
        assert s.debug is True

    def test_default_log_level(self) -> None:
        s = Settings()
        assert s.log_level == "INFO"

    def test_singleton_instance(self) -> None:
        assert settings.database_url is not None
