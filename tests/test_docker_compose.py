from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_PATH = ROOT / "docker-compose.yml"


@pytest.fixture
def compose() -> dict:
    return yaml.safe_load(COMPOSE_PATH.read_text())


class TestComposeFileExists:
    def test_file_exists(self) -> None:
        assert COMPOSE_PATH.exists()


class TestDbService:
    def test_image(self, compose: dict) -> None:
        assert compose["services"]["db"]["image"] == "postgres:16-alpine"

    def test_port_mapping(self, compose: dict) -> None:
        assert "5434:5432" in compose["services"]["db"]["ports"]

    def test_volume(self, compose: dict) -> None:
        assert "pgdata:/var/lib/postgresql/data" in compose["services"]["db"]["volumes"]

    def test_healthcheck(self, compose: dict) -> None:
        hc = compose["services"]["db"]["healthcheck"]
        assert "pg_isready" in hc["test"][-1]

    def test_env_from_file(self, compose: dict) -> None:
        env = compose["services"]["db"]["environment"]
        assert "POSTGRES_USER" in env or "${POSTGRES_USER}" in str(env)


class TestBackendService:
    def test_build_context(self, compose: dict) -> None:
        assert compose["services"]["backend"]["build"]["context"] == "./backend"

    def test_port_mapping(self, compose: dict) -> None:
        assert "8000:8000" in compose["services"]["backend"]["ports"]

    def test_depends_on_db(self, compose: dict) -> None:
        deps = compose["services"]["backend"]["depends_on"]
        assert "db" in deps
        assert deps["db"]["condition"] == "service_healthy"

    def test_healthcheck(self, compose: dict) -> None:
        hc = compose["services"]["backend"]["healthcheck"]
        assert hc is not None


class TestFrontendService:
    def test_build_context(self, compose: dict) -> None:
        assert compose["services"]["frontend"]["build"]["context"] == "./frontend"

    def test_port_mapping(self, compose: dict) -> None:
        assert "3000:80" in compose["services"]["frontend"]["ports"]

    def test_depends_on_backend(self, compose: dict) -> None:
        deps = compose["services"]["frontend"]["depends_on"]
        assert "backend" in deps
        assert deps["backend"]["condition"] == "service_healthy"


class TestVolumes:
    def test_pgdata_defined(self, compose: dict) -> None:
        assert "pgdata" in compose.get("volumes", {})
