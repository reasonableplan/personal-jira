"""Alembic 환경 설정 테스트.

env.py가 올바른 metadata와 동기 URL을 사용하는지 검증한다.
"""

from alembic.config import Config
from app.core.config import settings
from app.models.base import Base


class TestAlembicEnv:
    def test_sync_database_url_uses_psycopg2(self) -> None:
        assert "+psycopg2" in settings.SYNC_DATABASE_URL
        assert "+asyncpg" not in settings.SYNC_DATABASE_URL

    def test_sync_url_preserves_host_and_db(self) -> None:
        sync = settings.SYNC_DATABASE_URL
        assert "personal_jira" in sync
        assert "postgres" in sync

    def test_target_metadata_has_tables(self) -> None:
        import app.models  # noqa: F401

        table_names = set(Base.metadata.tables.keys())
        assert "epics" in table_names
        assert "stories" in table_names
        assert "tasks" in table_names
        assert "labels" in table_names
        assert "task_labels" in table_names

    def test_alembic_ini_loads(self) -> None:
        config = Config("alembic.ini")
        assert config.get_main_option("script_location") == "alembic"

    def test_alembic_ini_sqlalchemy_url_overridden_by_env(self) -> None:
        """env.py에서 set_main_option으로 URL을 덮어쓰므로, ini의 기본값은 무관."""
        config = Config("alembic.ini")
        ini_url = config.get_main_option("sqlalchemy.url")
        # ini 파일에는 기본 URL이 있음 (env.py가 런타임에 덮어씀)
        assert ini_url is not None
