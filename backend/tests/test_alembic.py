from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


class TestAlembicSetup:
    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND / "alembic.ini").is_file()

    def test_alembic_env_exists(self) -> None:
        assert (BACKEND / "alembic" / "env.py").is_file()

    def test_alembic_env_uses_database_url(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )
        assert "DATABASE_URL" in content or "database_url" in content

    def test_alembic_env_imports_base(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )
        assert "Base" in content or "target_metadata" in content

    def test_versions_dir_exists(self) -> None:
        assert (BACKEND / "alembic" / "versions").is_dir()
