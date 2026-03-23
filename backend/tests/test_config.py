from personal_jira.config import Settings


class TestSettings:
    def test_default_app_name(self) -> None:
        settings = Settings()
        assert settings.APP_NAME == "personal-jira"

    def test_default_debug_false(self) -> None:
        settings = Settings()
        assert settings.DEBUG is False

    def test_default_database_url(self) -> None:
        settings = Settings()
        assert "postgresql+asyncpg" in settings.DATABASE_URL

    def test_settings_is_singleton_pattern(self) -> None:
        from personal_jira.config import get_settings

        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
