from pathlib import Path

import pytest

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
GITIGNORE_PATH: Path = ROOT_DIR / ".gitignore"

PYTHON_PATTERNS: list[str] = [
    "__pycache__/",
    "*.py[cod]",
    "*.egg-info/",
    "*.egg",
    "dist/",
    "build/",
    ".venv/",
    "venv/",
    "*.whl",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
    "htmlcov/",
    ".coverage",
    "*.pyo",
]

NODE_PATTERNS: list[str] = [
    "node_modules/",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    ".npm",
]

IDE_PATTERNS: list[str] = [
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
    "*.sublime-project",
    "*.sublime-workspace",
]

ENV_PATTERNS: list[str] = [
    ".env",
    ".env.local",
    "*.log",
]


class TestGitignoreExists:
    def test_gitignore_file_exists(self) -> None:
        assert GITIGNORE_PATH.exists(), ".gitignore must exist at project root"

    def test_gitignore_is_not_empty(self) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, ".gitignore must not be empty"


class TestPythonPatterns:
    @pytest.mark.parametrize("pattern", PYTHON_PATTERNS)
    def test_contains_python_pattern(self, pattern: str) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert pattern in content, f"Missing Python pattern: {pattern}"


class TestNodePatterns:
    @pytest.mark.parametrize("pattern", NODE_PATTERNS)
    def test_contains_node_pattern(self, pattern: str) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert pattern in content, f"Missing Node pattern: {pattern}"


class TestIDEPatterns:
    @pytest.mark.parametrize("pattern", IDE_PATTERNS)
    def test_contains_ide_pattern(self, pattern: str) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert pattern in content, f"Missing IDE pattern: {pattern}"


class TestEnvPatterns:
    @pytest.mark.parametrize("pattern", ENV_PATTERNS)
    def test_contains_env_pattern(self, pattern: str) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert pattern in content, f"Missing env pattern: {pattern}"


class TestGitignoreSections:
    def test_has_section_headers(self) -> None:
        content = GITIGNORE_PATH.read_text(encoding="utf-8")
        assert "# Python" in content
        assert "# Node" in content
        assert "# IDE" in content
