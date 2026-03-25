from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


class TestAlembicSetup:
    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND / "alembic.ini").is_file()

    def test_alembic_env_exists(self) -> None:
        assert (BACKEND / "alembic" / "env.py").is_file()

    def test_alembic_env_uses_config_database_url(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "settings.database_url" in content or "config.database_url" in content.lower()

    def test_alembic_env_imports_base(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "Base" in content
        assert "target_metadata" in content

    def test_alembic_env_imports_all_models(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "app.models" in content

    def test_versions_dir_exists(self) -> None:
        assert (BACKEND / "alembic" / "versions").is_dir()

    def test_initial_migration_exists(self) -> None:
        versions = list((BACKEND / "alembic" / "versions").glob("*.py"))
        assert len(versions) >= 1

    def test_initial_migration_has_all_tables(self) -> None:
        versions = list((BACKEND / "alembic" / "versions").glob("*.py"))
        content = ""
        for v in versions:
            content += v.read_text(encoding="utf-8")
        for table in ["epics", "stories", "tasks", "labels", "task_labels", "activities", "agents"]:
            assert table in content, f"Table '{table}' not found in migration"

    def test_migration_has_indexes(self) -> None:
        versions = list((BACKEND / "alembic" / "versions").glob("*.py"))
        content = ""
        for v in versions:
            content += v.read_text(encoding="utf-8")
        for idx in [
            "ix_stories_epic_id_sort_order",
            "ix_tasks_story_id",
            "ix_tasks_board_column",
            "ix_tasks_assigned_agent",
            "ix_activities_task_id_created_at",
            "ix_agents_status",
        ]:
            assert idx in content, f"Index '{idx}' not found in migration"

    def test_migration_has_foreign_keys(self) -> None:
        versions = list((BACKEND / "alembic" / "versions").glob("*.py"))
        content = ""
        for v in versions:
            content += v.read_text(encoding="utf-8")
        assert "sa.ForeignKey" in content or "sa.ForeignKeyConstraint" in content or "foreign_keys" in content.lower()

    def test_alembic_ini_url_is_placeholder(self) -> None:
        content = (BACKEND / "alembic.ini").read_text(encoding="utf-8")
        assert "sqlalchemy.url" in content
