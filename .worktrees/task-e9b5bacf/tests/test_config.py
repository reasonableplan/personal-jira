import os
from unittest.mock import patch

import pytest


def test_settings_defaults():
    from app.config import Settings

    settings = Settings(DATABASE_URL="postgresql+asyncpg://u:p@localhost/db")
    assert settings.APP_NAME == "Personal Jira"
    assert settings.DEBUG is False


def test_settings_from_env():
    with patch.dict(os.environ, {
        "DATABASE_URL": "postgresql+asyncpg://test:test@db:5432/testdb",
        "APP_NAME": "Test App",
        "DEBUG": "true",
    }):
        from importlib import reload

        import app.config
        reload(app.config)
        settings = app.config.Settings()
        assert settings.DATABASE_URL == "postgresql+asyncpg://test:test@db:5432/testdb"
        assert settings.APP_NAME == "Test App"
        assert settings.DEBUG is True


def test_settings_database_url_required():
    with patch.dict(os.environ, {}, clear=True):
        from importlib import reload

        import app.config
        reload(app.config)
        with pytest.raises(Exception):
            app.config.Settings()
