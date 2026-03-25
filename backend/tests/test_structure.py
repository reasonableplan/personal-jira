from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
APP = BACKEND / "app"


class TestBackendStructure:
    def test_app_package(self) -> None:
        assert (APP / "__init__.py").is_file()

    def test_main_module(self) -> None:
        assert (APP / "main.py").is_file()

    def test_config_module(self) -> None:
        assert (APP / "config.py").is_file()

    def test_database_module(self) -> None:
        assert (APP / "database.py").is_file()

    def test_models_package(self) -> None:
        assert (APP / "models" / "__init__.py").is_file()

    def test_routers_package(self) -> None:
        assert (APP / "routers" / "__init__.py").is_file()

    def test_schemas_package(self) -> None:
        assert (APP / "schemas" / "__init__.py").is_file()

    def test_dockerfile(self) -> None:
        assert (BACKEND / "Dockerfile").is_file()

    def test_pyproject_toml(self) -> None:
        assert (BACKEND / "pyproject.toml").is_file()

    def test_exceptions_module(self) -> None:
        assert (APP / "exceptions.py").is_file()
