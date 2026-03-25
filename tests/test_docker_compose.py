import pytest
import yaml


@pytest.fixture
def compose_config() -> dict:
    with open("docker-compose.yml") as f:
        return yaml.safe_load(f)


class TestComposeStructure:
    def test_has_three_services(self, compose_config: dict) -> None:
        assert set(compose_config["services"].keys()) == {"db", "backend", "frontend"}

    def test_has_pgdata_volume(self, compose_config: dict) -> None:
        assert "pgdata" in compose_config["volumes"]


class TestDbService:
    def test_image(self, compose_config: dict) -> None:
        db = compose_config["services"]["db"]
        assert db["image"] == "postgres:16-alpine"

    def test_port_mapping(self, compose_config: dict) -> None:
        db = compose_config["services"]["db"]
        assert "5434:5432" in db["ports"]

    def test_environment_variables(self, compose_config: dict) -> None:
        db = compose_config["services"]["db"]
        env = db["environment"]
        assert env["POSTGRES_USER"] == "personal_jira"
        assert env["POSTGRES_PASSWORD"] == "personal_jira"
        assert env["POSTGRES_DB"] == "personal_jira"

    def test_named_volume(self, compose_config: dict) -> None:
        db = compose_config["services"]["db"]
        assert "pgdata:/var/lib/postgresql/data" in db["volumes"]
        assert "pgdata" in compose_config["volumes"]

    def test_healthcheck(self, compose_config: dict) -> None:
        db = compose_config["services"]["db"]
        assert "healthcheck" in db


class TestBackendService:
    def test_build_context(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        assert backend["build"]["context"] == "./backend"
        assert backend["build"]["dockerfile"] == "Dockerfile"

    def test_port_mapping(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        assert "8000:8000" in backend["ports"]

    def test_depends_on_db_healthy(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        assert backend["depends_on"]["db"]["condition"] == "service_healthy"

    def test_environment_has_database_url(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        env = backend["environment"]
        assert "DATABASE_URL" in env
        assert "asyncpg" in env["DATABASE_URL"]

    def test_environment_has_cors(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        env = backend["environment"]
        assert "CORS_ORIGINS" in env

    def test_healthcheck(self, compose_config: dict) -> None:
        backend = compose_config["services"]["backend"]
        assert "healthcheck" in backend


class TestFrontendService:
    def test_build_context(self, compose_config: dict) -> None:
        frontend = compose_config["services"]["frontend"]
        assert frontend["build"]["context"] == "./frontend"
        assert frontend["build"]["dockerfile"] == "Dockerfile"

    def test_port_mapping(self, compose_config: dict) -> None:
        frontend = compose_config["services"]["frontend"]
        assert "3000:80" in frontend["ports"]

    def test_depends_on_backend_healthy(self, compose_config: dict) -> None:
        frontend = compose_config["services"]["frontend"]
        assert frontend["depends_on"]["backend"]["condition"] == "service_healthy"


class TestBackendDockerfile:
    def test_dockerfile_exists(self) -> None:
        with open("backend/Dockerfile") as f:
            content = f.read()
        assert "python:3.12-slim" in content
        assert "uv" in content
        assert "uvicorn" in content

    def test_entrypoint_exists(self) -> None:
        with open("backend/entrypoint.sh") as f:
            content = f.read()
        assert "alembic upgrade head" in content
        assert "uvicorn" in content


class TestFrontendDockerfile:
    def test_dockerfile_exists(self) -> None:
        with open("frontend/Dockerfile") as f:
            content = f.read()
        assert "node" in content
        assert "nginx" in content


class TestEnvExample:
    def test_env_example_exists(self) -> None:
        with open(".env.example") as f:
            content = f.read()
        assert "DATABASE_URL" in content
        assert "POSTGRES_USER" in content
        assert "POSTGRES_PASSWORD" in content
        assert "POSTGRES_DB" in content
