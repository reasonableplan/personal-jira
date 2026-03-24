from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = ["backend", "frontend", ".github"]
REQUIRED_FILES = [".gitignore", "README.md", ".editorconfig", ".env.example"]


class TestDirectoryStructure:
    @pytest.mark.parametrize("dirname", REQUIRED_DIRS)
    def test_required_directories_exist(self, dirname: str) -> None:
        d = PROJECT_ROOT / dirname
        assert d.exists(), f"Missing directory: {dirname}"
        assert d.is_dir(), f"Not a directory: {dirname}"

    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_required_files_exist(self, filename: str) -> None:
        f = PROJECT_ROOT / filename
        assert f.exists(), f"Missing file: {filename}"
        assert f.is_file(), f"Not a file: {filename}"


class TestGitignore:
    @pytest.fixture()
    def gitignore_content(self) -> str:
        return (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "pattern",
        ["__pycache__", ".venv", "*.pyc", ".env", "node_modules", "dist", ".vscode", ".idea", ".DS_Store", "Thumbs.db", "docker-compose.override.yml"],
    )
    def test_gitignore_contains_pattern(self, gitignore_content: str, pattern: str) -> None:
        assert pattern in gitignore_content, f"Missing .gitignore pattern: {pattern}"


class TestEditorconfig:
    def test_editorconfig_exists_and_valid(self) -> None:
        ec = PROJECT_ROOT / ".editorconfig"
        content = ec.read_text(encoding="utf-8")
        assert "root = true" in content
        assert "indent_style" in content
        assert "charset" in content


class TestEnvExample:
    @pytest.fixture()
    def env_content(self) -> str:
        return (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "var",
        ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_PORT"],
    )
    def test_env_example_contains_variable(self, env_content: str, var: str) -> None:
        assert var in env_content, f"Missing env variable: {var}"

    def test_postgres_port_default(self, env_content: str) -> None:
        assert "POSTGRES_PORT=5434" in env_content


class TestReadme:
    def test_readme_has_content(self) -> None:
        readme = PROJECT_ROOT / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert len(content) > 100
        assert "backend" in content.lower()
        assert "frontend" in content.lower()
