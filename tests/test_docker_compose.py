"""Tests for Docker Compose configuration and .env.example."""

import pathlib
import re

import pytest
import yaml

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

DOCKER_COMPOSE_FILE = "docker-compose.yml"
ENV_EXAMPLE_FILE = ".env.example"

REQUIRED_ENV_VARS: list[str] = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_PORT",
]


@pytest.fixture()
def compose_path() -> pathlib.Path:
    path = PROJECT_ROOT / DOCKER_COMPOSE_FILE
    assert path.exists(), f"{DOCKER_COMPOSE_FILE} must exist at project root"
    return path


@pytest.fixture()
def compose_data(compose_path: pathlib.Path) -> dict:
    content = compose_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    assert isinstance(data, dict), "docker-compose.yml must be a valid YAML mapping"
    return data


@pytest.fixture()
def env_example_path() -> pathlib.Path:
    path = PROJECT_ROOT / ENV_EXAMPLE_FILE
    assert path.exists(), f"{ENV_EXAMPLE_FILE} must exist at project root"
    return path


@pytest.fixture()
def env_example_content(env_example_path: pathlib.Path) -> str:
    return env_example_path.read_text(encoding="utf-8")


class TestDockerComposeStructure:
    """Verify top-level docker-compose.yml structure."""

    def test_services_key_exists(self, compose_data: dict) -> None:
        assert "services" in compose_data, "Top-level 'services' key must exist"

    def test_volumes_key_exists(self, compose_data: dict) -> None:
        assert "volumes" in compose_data, "Top-level 'volumes' key must exist"

    def test_postgres_data_volume_defined(self, compose_data: dict) -> None:
        volumes = compose_data.get("volumes", {})
        assert "postgres_data" in volumes, "Named volume 'postgres_data' must be defined"


class TestPostgresService:
    """Verify PostgreSQL 16 service configuration."""

    @pytest.fixture()
    def postgres_service(self, compose_data: dict) -> dict:
        services = compose_data.get("services", {})
        assert "db" in services, "Service 'db' must be defined"
        return services["db"]

    def test_postgres_image_is_version_16(
        self, postgres_service: dict
    ) -> None:
        image = postgres_service.get("image", "")
        assert re.match(r"postgres:16", image), (
            f"PostgreSQL image must be version 16, got: {image}"
        )

    def test_postgres_container_name(
        self, postgres_service: dict
    ) -> None:
        assert "container_name" in postgres_service, (
            "container_name must be set for the db service"
        )

    def test_postgres_restart_policy(
        self, postgres_service: dict
    ) -> None:
        restart = postgres_service.get("restart", "")
        assert restart == "unless-stopped", (
            f"restart policy must be 'unless-stopped', got: {restart}"
        )

    def test_postgres_env_file_configured(
        self, postgres_service: dict
    ) -> None:
        env_file = postgres_service.get("env_file")
        assert env_file is not None, "env_file must be configured"
        if isinstance(env_file, list):
            assert ".env" in env_file, "env_file must reference .env"
        else:
            assert env_file == ".env", "env_file must reference .env"

    def test_postgres_ports_mapping(
        self, postgres_service: dict
    ) -> None:
        ports = postgres_service.get("ports", [])
        assert len(ports) > 0, "At least one port mapping must be defined"
        port_str = str(ports[0])
        assert "5432" in port_str, "Port mapping must include PostgreSQL default port 5432"

    def test_postgres_volume_mount(
        self, postgres_service: dict
    ) -> None:
        volumes = postgres_service.get("volumes", [])
        assert len(volumes) > 0, "At least one volume must be mounted"
        volume_str = str(volumes[0])
        assert "postgres_data" in volume_str, "Volume must reference 'postgres_data'"
        assert "/var/lib/postgresql/data" in volume_str, (
            "Volume must mount to /var/lib/postgresql/data"
        )

    def test_postgres_healthcheck_defined(
        self, postgres_service: dict
    ) -> None:
        assert "healthcheck" in postgres_service, (
            "healthcheck must be defined for the db service"
        )

    def test_postgres_healthcheck_uses_pg_isready(
        self, postgres_service: dict
    ) -> None:
        healthcheck = postgres_service.get("healthcheck", {})
        test_cmd = healthcheck.get("test", [])
        test_str = " ".join(test_cmd) if isinstance(test_cmd, list) else str(test_cmd)
        assert "pg_isready" in test_str, "healthcheck must use pg_isready"

    def test_postgres_healthcheck_has_required_fields(
        self, postgres_service: dict
    ) -> None:
        healthcheck = postgres_service.get("healthcheck", {})
        required_fields = ["test", "interval", "timeout", "retries", "start_period"]
        for field in required_fields:
            assert field in healthcheck, f"healthcheck must include '{field}'"


class TestEnvExample:
    """Verify .env.example contains required variables."""

    def test_required_env_vars_present(
        self, env_example_content: str
    ) -> None:
        for var in REQUIRED_ENV_VARS:
            assert var in env_example_content, (
                f"{var} must be defined in {ENV_EXAMPLE_FILE}"
            )

    def test_no_real_secrets_in_env_example(
        self, env_example_content: str
    ) -> None:
        for line in env_example_content.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                value = line.split("=", 1)[1].strip()
                assert value == "" or value.startswith("your_") or value.isdigit(), (
                    f"Suspicious value in .env.example: '{line}'. "
                    "Use empty values or 'your_*' placeholders"
                )

    def test_database_url_no_variable_interpolation(
        self, env_example_content: str
    ) -> None:
        for line in env_example_content.strip().splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            assert "${" not in line, (
                "DATABASE_URL must not use variable interpolation"
            )
