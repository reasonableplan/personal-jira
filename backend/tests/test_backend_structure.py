from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "pyproject.toml",
    "Dockerfile",
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/database.py",
    "app/models/__init__.py",
    "app/schemas/__init__.py",
    "app/routers/__init__.py",
]


class TestBackendStructure:
    @pytest.mark.parametrize("relpath", REQUIRED_FILES)
    def test_required_file_exists(self, relpath: str) -> None:
        assert (BACKEND_ROOT / relpath).exists(), f"{relpath} missing"

    def test_pyproject_contains_fastapi(self) -> None:
        content = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "fastapi" in content

    def test_dockerfile_uses_python312(self) -> None:
        content = (BACKEND_ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "python:3.12" in content
