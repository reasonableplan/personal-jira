from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
APP = BACKEND / "app"


class TestBackendStructure:
    def test_app_package(self) -> None:
        assert (APP / "__init__.py").exists()

    def test_main_module(self) -> None:
        assert (APP / "main.py").exists()

    def test_config_module(self) -> None:
        assert (APP / "config.py").exists()

    def test_database_module(self) -> None:
        assert (APP / "database.py").exists()

    def test_models_package(self) -> None:
        assert (APP / "models" / "__init__.py").exists()

    def test_routers_package(self) -> None:
        assert (APP / "routers" / "__init__.py").exists()

    def test_schemas_package(self) -> None:
        assert (APP / "schemas" / "__init__.py").exists()

    def test_pyproject_toml(self) -> None:
        assert (BACKEND / "pyproject.toml").exists()

    def test_dockerfile(self) -> None:
        assert (BACKEND / "Dockerfile").exists()

    def test_alembic_ini(self) -> None:
        assert (BACKEND / "alembic.ini").exists()

    def test_alembic_env(self) -> None:
        assert (BACKEND / "alembic" / "env.py").exists()
