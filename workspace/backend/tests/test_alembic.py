"""Alembic 설정 및 마이그레이션 테스트."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.models.base import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _get_alembic_config() -> Config:
    ini_path = BACKEND_DIR / "alembic.ini"
    cfg = Config(str(ini_path))
    return cfg


class TestAlembicConfig:
    def test_alembic_ini_sqlalchemy_url_is_empty(self):
        cfg = _get_alembic_config()
        url = cfg.get_main_option("sqlalchemy.url")
        assert url == "", f"alembic.ini sqlalchemy.url should be empty, got: {url!r}"

    def test_script_location_exists(self):
        alembic_dir = BACKEND_DIR / "alembic"
        assert alembic_dir.is_dir()
        assert (alembic_dir / "env.py").is_file()
        assert (alembic_dir / "versions").is_dir()

    def test_initial_migration_exists(self):
        cfg = _get_alembic_config()
        script = ScriptDirectory.from_config(cfg)
        revisions = list(script.walk_revisions())
        assert len(revisions) >= 1
        initial = revisions[-1]
        assert initial.down_revision is None
        assert "initial_tables" in (initial.doc or "")


class TestEnvPyConfig:
    def test_env_uses_settings_database_url(self):
        """env.py가 settings.DATABASE_URL을 사용하는지 확인."""
        env_path = BACKEND_DIR / "alembic" / "env.py"
        content = env_path.read_text(encoding="utf-8")
        assert "from app.core.config import settings" in content
        assert "settings.DATABASE_URL" in content

    def test_env_uses_async_engine(self):
        """env.py가 async engine을 사용하는지 확인."""
        env_path = BACKEND_DIR / "alembic" / "env.py"
        content = env_path.read_text(encoding="utf-8")
        assert "async_engine_from_config" in content
        assert "run_async_migrations" in content

    def test_env_imports_base_metadata(self):
        """env.py가 Base.metadata를 target_metadata로 설정하는지 확인."""
        env_path = BACKEND_DIR / "alembic" / "env.py"
        content = env_path.read_text(encoding="utf-8")
        assert "from app.models import Base" in content
        assert "target_metadata = Base.metadata" in content


class TestModelTables:
    def test_all_tables_registered_in_metadata(self):
        expected_tables = {"epics", "stories", "tasks", "labels", "task_labels"}
        actual_tables = set(Base.metadata.tables.keys())
        assert expected_tables.issubset(actual_tables), (
            f"Missing tables: {expected_tables - actual_tables}"
        )

    def test_tasks_indexes(self):
        tasks_table = Base.metadata.tables["tasks"]
        index_names = {idx.name for idx in tasks_table.indexes}
        assert "ix_tasks_status" in index_names
        assert "ix_tasks_priority" in index_names
        assert "ix_tasks_story_id" in index_names

    def test_stories_indexes(self):
        stories_table = Base.metadata.tables["stories"]
        index_names = {idx.name for idx in stories_table.indexes}
        assert "ix_stories_epic_id" in index_names

    def test_labels_name_unique(self):
        labels_table = Base.metadata.tables["labels"]
        name_col = labels_table.c.name
        assert name_col.unique is True
