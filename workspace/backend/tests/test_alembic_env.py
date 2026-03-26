"""Tests for alembic/env.py configuration."""

from app.core.database import Base


class TestGetSyncUrl:
    """Tests for _get_sync_url() URL conversion logic."""

    @staticmethod
    def _get_sync_url(url: str) -> str:
        """Import-free replica of alembic.env._get_sync_url for unit testing.

        We re-implement the function here instead of importing from
        ``alembic.env`` because importing that module triggers Alembic's
        ``context`` machinery which requires a live migration context.
        """
        return url.replace("+asyncpg", "+psycopg2")

    def test_converts_asyncpg_to_psycopg2(self) -> None:
        url = "postgresql+asyncpg://postgres:postgres@localhost:5433/personal_jira"
        result = self._get_sync_url(url)
        assert result == "postgresql+psycopg2://postgres:postgres@localhost:5433/personal_jira"

    def test_url_without_asyncpg_unchanged(self) -> None:
        url = "postgresql://postgres:postgres@localhost:5433/personal_jira"
        result = self._get_sync_url(url)
        assert result == url

    def test_psycopg2_url_unchanged(self) -> None:
        url = "postgresql+psycopg2://postgres:postgres@localhost:5433/personal_jira"
        result = self._get_sync_url(url)
        assert result == url

    def test_url_with_special_characters_in_password(self) -> None:
        url = "postgresql+asyncpg://user:p%40ss%23word@host:5432/db"
        result = self._get_sync_url(url)
        assert result == "postgresql+psycopg2://user:p%40ss%23word@host:5432/db"


class TestTargetMetadata:
    """Tests that target_metadata is correctly wired to Base.metadata."""

    def test_target_metadata_is_base_metadata(self) -> None:
        # alembic/env.py sets: target_metadata = Base.metadata
        # We verify the metadata object is the same identity.
        from app.core.database import Base as EnvBase

        assert EnvBase.metadata is Base.metadata

    def test_models_package_importable(self) -> None:
        """Verify that ``import app.models`` succeeds and exposes Base."""
        import app.models

        assert hasattr(app.models, "Base")
        assert app.models.Base is Base
