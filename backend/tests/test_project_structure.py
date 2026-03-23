from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "src/personal_jira",
    "src/personal_jira/api",
    "src/personal_jira/models",
    "src/personal_jira/schemas",
    "src/personal_jira/services",
    "tests",
    "alembic",
    "alembic/versions",
    "docker",
]

REQUIRED_FILES = [
    "pyproject.toml",
    ".gitignore",
    ".env.example",
    "alembic.ini",
    "alembic/env.py",
    "alembic/versions/.gitkeep",
    "docker/.gitkeep",
    "src/personal_jira/__init__.py",
    "src/personal_jira/py.typed",
    "src/personal_jira/app.py",
    "src/personal_jira/config.py",
    "src/personal_jira/database.py",
    "src/personal_jira/api/__init__.py",
    "src/personal_jira/api/health.py",
    "src/personal_jira/models/__init__.py",
    "src/personal_jira/schemas/__init__.py",
    "src/personal_jira/services/__init__.py",
    "tests/__init__.py",
    "tests/conftest.py",
]


class TestDirectoryStructure:
    @pytest.mark.parametrize("dir_path", REQUIRED_DIRS)
    def test_required_directory_exists(self, dir_path: str) -> None:
        assert (ROOT / dir_path).is_dir(), f"Missing directory: {dir_path}"


class TestRequiredFiles:
    @pytest.mark.parametrize("file_path", REQUIRED_FILES)
    def test_required_file_exists(self, file_path: str) -> None:
        assert (ROOT / file_path).is_file(), f"Missing file: {file_path}"


class TestGitignore:
    def test_gitignore_contains_patterns(self) -> None:
        content = (ROOT / ".gitignore").read_text()
        for pattern in ["__pycache__", ".env", "*.pyc", ".venv", "dist/"]:
            assert pattern in content, f"Missing .gitignore pattern: {pattern}"


class TestPyprojectToml:
    def test_pyproject_has_project_name(self) -> None:
        content = (ROOT / "pyproject.toml").read_text()
        assert 'name = "personal-jira"' in content

    def test_pyproject_has_dependencies(self) -> None:
        content = (ROOT / "pyproject.toml").read_text()
        for dep in ["fastapi", "uvicorn", "sqlalchemy", "asyncpg", "alembic", "pydantic"]:
            assert dep in content, f"Missing dependency: {dep}"

    def test_pyproject_has_python_requires(self) -> None:
        content = (ROOT / "pyproject.toml").read_text()
        assert "requires-python" in content

    def test_pyproject_has_build_system(self) -> None:
        content = (ROOT / "pyproject.toml").read_text()
        assert "[build-system]" in content
        assert "hatchling" in content


class TestAlembicConfig:
    def test_alembic_ini_references_env(self) -> None:
        content = (ROOT / "alembic.ini").read_text()
        assert "alembic" in content

    def test_alembic_env_imports_models(self) -> None:
        content = (ROOT / "alembic/env.py").read_text()
        assert "target_metadata" in content


class TestSrcLayout:
    def test_app_has_create_app(self) -> None:
        content = (ROOT / "src/personal_jira/app.py").read_text()
        assert "create_app" in content

    def test_config_has_settings(self) -> None:
        content = (ROOT / "src/personal_jira/config.py").read_text()
        assert "Settings" in content

    def test_database_has_engine(self) -> None:
        content = (ROOT / "src/personal_jira/database.py").read_text()
        assert "engine" in content

    def test_health_router_exists(self) -> None:
        content = (ROOT / "src/personal_jira/api/health.py").read_text()
        assert "router" in content
