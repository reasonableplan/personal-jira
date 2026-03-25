from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


class TestProjectStructure:
    def test_pyproject_toml_exists(self) -> None:
        assert (BACKEND / "pyproject.toml").exists()

    def test_app_package_exists(self) -> None:
        assert (BACKEND / "app" / "__init__.py").exists()

    def test_models_package_exists(self) -> None:
        assert (BACKEND / "app" / "models" / "__init__.py").exists()

    def test_routers_package_exists(self) -> None:
        assert (BACKEND / "app" / "routers" / "__init__.py").exists()

    def test_schemas_package_exists(self) -> None:
        assert (BACKEND / "app" / "schemas" / "__init__.py").exists()

    def test_dockerfile_exists(self) -> None:
        assert (BACKEND / "Dockerfile").exists()

    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND / "alembic.ini").exists()

    def test_alembic_env_exists(self) -> None:
        assert (BACKEND / "alembic" / "env.py").exists()
