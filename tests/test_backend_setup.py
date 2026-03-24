import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"


class TestPyprojectToml:
    def test_exists(self) -> None:
        assert (BACKEND / "pyproject.toml").exists()

    def test_has_required_dependencies(self) -> None:
        with open(BACKEND / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        deps = data["project"]["dependencies"]
        required = ["fastapi", "uvicorn", "sqlalchemy", "alembic", "psycopg2-binary", "pydantic-settings"]
        for pkg in required:
            assert any(pkg in d for d in deps), f"{pkg} missing from dependencies"

    def test_project_name(self) -> None:
        with open(BACKEND / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        assert data["project"]["name"] == "personal-jira-backend"

    def test_python_version(self) -> None:
        with open(BACKEND / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        assert "requires-python" in data["project"]


class TestAppPackageStructure:
    def test_app_package_exists(self) -> None:
        assert (BACKEND / "app").is_dir()
        assert (BACKEND / "app" / "__init__.py").exists()

    def test_main_module(self) -> None:
        assert (BACKEND / "app" / "main.py").exists()

    def test_config_module(self) -> None:
        assert (BACKEND / "app" / "config.py").exists()

    def test_db_module(self) -> None:
        assert (BACKEND / "app" / "db.py").exists()

    def test_subpackages(self) -> None:
        for pkg in ["models", "routers", "schemas"]:
            assert (BACKEND / "app" / pkg).is_dir(), f"{pkg}/ missing"
            assert (BACKEND / "app" / pkg / "__init__.py").exists(), f"{pkg}/__init__.py missing"


class TestAlembicSetup:
    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND / "alembic.ini").exists()

    def test_alembic_env_exists(self) -> None:
        assert (BACKEND / "alembic" / "env.py").exists()

    def test_alembic_versions_dir(self) -> None:
        assert (BACKEND / "alembic" / "versions").is_dir()

    def test_alembic_env_uses_database_url(self) -> None:
        content = (BACKEND / "alembic" / "env.py").read_text(encoding="utf-8")
        assert "DATABASE_URL" in content


class TestHealthEndpoint:
    def test_main_imports(self) -> None:
        content = (BACKEND / "app" / "main.py").read_text(encoding="utf-8")
        assert "FastAPI" in content
        assert "/health" in content

    def test_config_uses_pydantic_settings(self) -> None:
        content = (BACKEND / "app" / "config.py").read_text(encoding="utf-8")
        assert "BaseSettings" in content
        assert "DATABASE_URL" in content or "database_url" in content

    def test_db_module_has_engine(self) -> None:
        content = (BACKEND / "app" / "db.py").read_text(encoding="utf-8")
        assert "engine" in content
        assert "Session" in content or "session" in content
