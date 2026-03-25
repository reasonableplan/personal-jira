import os


def test_settings_loads_defaults() -> None:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5434/personal_jira",
    )
    from app.config import settings

    assert settings.DATABASE_URL is not None
    assert "postgresql" in settings.DATABASE_URL


def test_settings_has_app_name() -> None:
    from app.config import settings

    assert settings.APP_NAME == "personal-jira"
