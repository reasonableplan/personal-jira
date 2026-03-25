from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent


class TestDockerComposeFile:
    @pytest.fixture(autouse=True)
    def load_compose(self) -> None:
        compose_path = ROOT / "docker-compose.yml"
        assert compose_path.exists(), "docker-compose.yml must exist at project root"
        with open(compose_path) as f:
            self.compose = yaml.safe_load(f)

    def test_has_three_services(self) -> None:
        services = self.compose["services"]
        assert "db" in services
        assert "backend" in services
        assert "frontend" in services

    def test_db_service_image(self) -> None:
        db = self.compose["services"]["db"]
        assert db["image"] == "postgres:16-alpine"

    def test_db_service_port(self) -> None:
        db = self.compose["services"]["db"]
        assert "5434:5432" in db["ports"]

    def test_db_service_volume(self) -> None:
        db = self.compose["services"]["db"]
        assert "pgdata:/var/lib/postgresql/data" in db["volumes"]

    def test_db_healthcheck(self) -> None:
        db = self.compose["services"]["db"]
        assert "healthcheck" in db
        hc = db["healthcheck"]
        assert any("pg_isready" in str(t) for t in hc["test"])

    def test_db_environment(self) -> None:
        db = self.compose["services"]["db"]
        env = db["environment"]
        assert env["POSTGRES_USER"] == "personal_jira"
        assert env["POSTGRES_PASSWORD"] == "personal_jira"
        assert env["POSTGRES_DB"] == "personal_jira"

    def test_backend_build_context(self) -> None:
        backend = self.compose["services"]["backend"]
        assert backend["build"]["context"] == "./backend"
        assert backend["build"]["dockerfile"] == "Dockerfile"

    def test_backend_port(self) -> None:
        backend = self.compose["services"]["backend"]
        assert "8000:8000" in backend["ports"]

    def test_backend_depends_on_db_healthy(self) -> None:
        backend = self.compose["services"]["backend"]
        deps = backend["depends_on"]
        assert deps["db"]["condition"] == "service_healthy"

    def test_backend_healthcheck(self) -> None:
        backend = self.compose["services"]["backend"]
        assert "healthcheck" in backend

    def test_backend_environment_has_database_url(self) -> None:
        backend = self.compose["services"]["backend"]
        env = backend["environment"]
        assert "DATABASE_URL" in env
        assert "asyncpg" in env["DATABASE_URL"]

    def test_frontend_build_context(self) -> None:
        frontend = self.compose["services"]["frontend"]
        assert frontend["build"]["context"] == "./frontend"
        assert frontend["build"]["dockerfile"] == "Dockerfile"

    def test_frontend_port(self) -> None:
        frontend = self.compose["services"]["frontend"]
        assert "3000:80" in frontend["ports"]

    def test_frontend_depends_on_backend_healthy(self) -> None:
        frontend = self.compose["services"]["frontend"]
        deps = frontend["depends_on"]
        assert deps["backend"]["condition"] == "service_healthy"

    def test_volumes_defined(self) -> None:
        assert "pgdata" in self.compose["volumes"]


class TestBackendDockerfile:
    @pytest.fixture(autouse=True)
    def load_dockerfile(self) -> None:
        self.dockerfile_path = ROOT / "backend" / "Dockerfile"
        assert self.dockerfile_path.exists(), "backend/Dockerfile must exist"
        self.content = self.dockerfile_path.read_text()

    def test_base_image_python312(self) -> None:
        assert "python:3.12-slim" in self.content

    def test_uses_uv(self) -> None:
        assert "uv" in self.content

    def test_runs_uvicorn(self) -> None:
        assert "uvicorn" in self.content

    def test_exposes_port_8000(self) -> None:
        assert "8000" in self.content

    def test_has_workdir(self) -> None:
        assert "WORKDIR" in self.content


class TestFrontendDockerfile:
    @pytest.fixture(autouse=True)
    def load_dockerfile(self) -> None:
        self.dockerfile_path = ROOT / "frontend" / "Dockerfile"
        assert self.dockerfile_path.exists(), "frontend/Dockerfile must exist"
        self.content = self.dockerfile_path.read_text()

    def test_multi_stage_build(self) -> None:
        assert self.content.count("FROM ") >= 2

    def test_node_build_stage(self) -> None:
        assert "node:20-alpine" in self.content

    def test_nginx_serve_stage(self) -> None:
        assert "nginx:alpine" in self.content

    def test_copies_nginx_conf(self) -> None:
        assert "nginx.conf" in self.content

    def test_exposes_port_80(self) -> None:
        assert "80" in self.content


class TestNginxConf:
    @pytest.fixture(autouse=True)
    def load_nginx(self) -> None:
        self.nginx_path = ROOT / "frontend" / "nginx.conf"
        assert self.nginx_path.exists(), "frontend/nginx.conf must exist"
        self.content = self.nginx_path.read_text()

    def test_has_api_proxy(self) -> None:
        assert "/api" in self.content
        assert "proxy_pass" in self.content

    def test_proxy_target_backend(self) -> None:
        assert "backend:8000" in self.content

    def test_spa_fallback(self) -> None:
        assert "try_files" in self.content
        assert "index.html" in self.content

    def test_listens_on_80(self) -> None:
        assert "listen" in self.content
        assert "80" in self.content


class TestEnvExample:
    def test_env_example_exists(self) -> None:
        env_path = ROOT / ".env.example"
        assert env_path.exists(), ".env.example must exist"
        content = env_path.read_text()
        assert "POSTGRES_USER" in content
        assert "POSTGRES_PASSWORD" in content
        assert "POSTGRES_DB" in content
        assert "DATABASE_URL" in content
