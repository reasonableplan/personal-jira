from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_pyproject_exists():
    assert (BACKEND_DIR / "pyproject.toml").exists()


def test_core_imports():
    import alembic
    import fastapi
    import pydantic_settings
    import sqlalchemy
    import uvicorn

    assert fastapi
    assert uvicorn
    assert sqlalchemy
    assert alembic
    assert pydantic_settings


def test_dev_imports():
    import httpx
    import pytest
    import ruff

    assert pytest
    assert httpx
    assert ruff


def test_app_import():
    from app.main import app

    assert app is not None
    assert app.title == "Personal Jira"


def test_database_import():
    from app.core.database import Base, get_db, get_engine

    assert Base is not None
    assert callable(get_db)
    assert callable(get_engine)


def test_config_import():
    from app.core.config import Settings

    assert Settings is not None
