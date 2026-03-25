import os
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPOSE_PATH = os.path.join(PROJECT_ROOT, "docker-compose.yml")
BACKEND_DOCKERFILE = os.path.join(PROJECT_ROOT, "backend", "Dockerfile")
FRONTEND_DOCKERFILE = os.path.join(PROJECT_ROOT, "frontend", "Dockerfile")
ENV_EXAMPLE = os.path.join(PROJECT_ROOT, ".env.example")
ENTRYPOINT = os.path.join(PROJECT_ROOT, "backend", "entrypoint.sh")


@pytest.fixture(scope="module")
def compose_config() -> dict:
    with open(COMPOSE_PATH) as f:
        return yaml.safe_load(f)


class TestComposeFileExists:
    def test_docker_compose_exists(self) -> None:
        assert os.path.isfile(COMPOSE_PATH)

    def test_backend_dockerfile_exists(self) -> None:
        assert os.path.isfile(BACKEND_DOCKERFILE)

    def test_frontend_dockerfile_exists(self) -> None:
        assert os.path.isfile(FRONTEND_DOCKERFILE)

    def test_env_example_exists(self) -> None:
        assert os.path.isfile(ENV_EXAMPLE)

    def test_entrypoint_exists(self) -> None:
        assert os.path.isfile(ENTRYPOINT)


class TestComposeServices:
    def test_has_three_services(self, compose_config: dict) -> None:
        assert len(compose_config["services"]) == 3

    def test_has_db_service(self, compose_config: dict) -> None:
        assert "db" in compose_config["services"]

    def test_has_backend_service(self, compose_config: dict) -> None:
        assert "backend" in compose_config["services"]

    def test_has_frontend_service(self, compose_config: dict) -> None:
        assert "frontend" in compose_config["services"]


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
        be = compose_config["services"]["backend"]
        assert be["build"]["context"] == "./backend"
        assert be["build"]["dockerfile"] == "Dockerfile"

    def test_port_mapping(self, compose_config: dict) -> None:
        be = compose_config["services"]["backend"]
        assert "8000:8000" in be["ports"]

    def test_depends_on_db_healthy(self, compose_config: dict) -> None:
        be = compose_config["services"]["backend"]
        assert be["depends_on"]["db"]["condition"] == "service_healthy"

    def test_database_url_env(self, compose_config: dict) -> None:
        be = compose_config["services"]["backend"]
        env = be["environment"]
        assert "DATABASE_URL" in env
        assert "asyncpg" in env["DATABASE_URL"]

    def test_healthcheck(self, compose_config: dict) -> None:
        be = compose_config["services"]["backend"]
        assert "healthcheck" in be


class TestFrontendService:
    def test_build_context(self, compose_config: dict) -> None:
        fe = compose_config["services"]["frontend"]
        assert fe["build"]["context"] == "./frontend"
        assert fe["build"]["dockerfile"] == "Dockerfile"

    def test_port_mapping(self, compose_config: dict) -> None:
        fe = compose_config["services"]["frontend"]
        assert "3000:80" in fe["ports"]

    def test_depends_on_backend(self, compose_config: dict) -> None:
        fe = compose_config["services"]["frontend"]
        assert "backend" in fe["depends_on"]


class TestBackendDockerfile:
    def test_uses_python_312_slim(self) -> None:
        with open(BACKEND_DOCKERFILE) as f:
            content = f.read()
        assert "python:3.12-slim" in content

    def test_uses_uv(self) -> None:
        with open(BACKEND_DOCKERFILE) as f:
            content = f.read()
        assert "uv" in content

    def test_exposes_8000(self) -> None:
        with open(BACKEND_DOCKERFILE) as f:
            content = f.read()
        assert "8000" in content

    def test_uses_entrypoint(self) -> None:
        with open(BACKEND_DOCKERFILE) as f:
            content = f.read()
        assert "entrypoint.sh" in content


class TestFrontendDockerfile:
    def test_uses_node_for_build(self) -> None:
        with open(FRONTEND_DOCKERFILE) as f:
            content = f.read()
        assert "node:" in content

    def test_uses_nginx_alpine(self) -> None:
        with open(FRONTEND_DOCKERFILE) as f:
            content = f.read()
        assert "nginx:alpine" in content


class TestEnvExample:
    def test_contains_database_url(self) -> None:
        with open(ENV_EXAMPLE) as f:
            content = f.read()
        assert "DATABASE_URL" in content

    def test_contains_postgres_user(self) -> None:
        with open(ENV_EXAMPLE) as f:
            content = f.read()
        assert "POSTGRES_USER" in content

    def test_contains_postgres_password(self) -> None:
        with open(ENV_EXAMPLE) as f:
            content = f.read()
        assert "POSTGRES_PASSWORD" in content

    def test_contains_postgres_db(self) -> None:
        with open(ENV_EXAMPLE) as f:
            content = f.read()
        assert "POSTGRES_DB" in content


class TestEntrypoint:
    def test_runs_alembic_upgrade(self) -> None:
        with open(ENTRYPOINT) as f:
            content = f.read()
        assert "alembic upgrade head" in content

    def test_runs_uvicorn(self) -> None:
        with open(ENTRYPOINT) as f:
            content = f.read()
        assert "uvicorn" in content

    def test_is_bash_script(self) -> None:
        with open(ENTRYPOINT) as f:
            first_line = f.readline()
        assert first_line.startswith("#!/")
