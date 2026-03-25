import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"
API_HEALTH_ENDPOINT = f"{FRONTEND_URL}/api/health"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5434

MAX_WAIT_SECONDS = 60
POLL_INTERVAL = 2


def _wait_for_http(url: str, timeout: int = MAX_WAIT_SECONDS) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(POLL_INTERVAL)
    return False


def _http_get(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, resp.read().decode("utf-8")


def _wait_for_tcp(host: str, port: int, timeout: int = MAX_WAIT_SECONDS) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=5):
                return True
        except (ConnectionRefusedError, OSError):
            pass
        time.sleep(POLL_INTERVAL)
    return False


@pytest.fixture(scope="module")
def docker_compose_up() -> None:
    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d", "--build", "--wait"],
        check=True,
        cwd=str(PROJECT_ROOT),
        timeout=300,
    )
    yield
    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "down", "-v", "--remove-orphans"],
        check=True,
        cwd=str(PROJECT_ROOT),
        timeout=120,
    )


class TestPostgresConnection:
    def test_postgres_accepts_connections(self, docker_compose_up: None) -> None:
        assert _wait_for_tcp(POSTGRES_HOST, POSTGRES_PORT), (
            f"PostgreSQL not responding on {POSTGRES_HOST}:{POSTGRES_PORT}"
        )

    def test_postgres_port_is_5434(self, docker_compose_up: None) -> None:
        _wait_for_tcp(POSTGRES_HOST, POSTGRES_PORT)
        with socket.create_connection((POSTGRES_HOST, POSTGRES_PORT), timeout=5) as sock:
            assert sock is not None


class TestBackendHealth:
    def test_backend_healthcheck_returns_200(self, docker_compose_up: None) -> None:
        assert _wait_for_http(HEALTH_ENDPOINT), (
            f"Backend health endpoint not responding at {HEALTH_ENDPOINT}"
        )
        status, body = _http_get(HEALTH_ENDPOINT)
        assert status == 200

    def test_backend_healthcheck_body(self, docker_compose_up: None) -> None:
        _wait_for_http(HEALTH_ENDPOINT)
        status, body = _http_get(HEALTH_ENDPOINT)
        data = json.loads(body)
        assert data == {"status": "ok"}


class TestFrontendServing:
    def test_frontend_returns_200(self, docker_compose_up: None) -> None:
        assert _wait_for_http(FRONTEND_URL), (
            f"Frontend not responding at {FRONTEND_URL}"
        )
        status, body = _http_get(FRONTEND_URL)
        assert status == 200

    def test_frontend_serves_html(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        status, body = _http_get(FRONTEND_URL)
        assert "<!doctype html>" in body.lower() or "<html" in body.lower()

    def test_frontend_serves_react_app(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        status, body = _http_get(FRONTEND_URL)
        assert '<div id="root">' in body or '<div id="app">' in body


class TestApiProxy:
    def test_frontend_proxies_api_health(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        _wait_for_http(HEALTH_ENDPOINT)
        assert _wait_for_http(API_HEALTH_ENDPOINT), (
            f"API proxy not working at {API_HEALTH_ENDPOINT}"
        )
        status, body = _http_get(API_HEALTH_ENDPOINT)
        assert status == 200
        data = json.loads(body)
        assert data == {"status": "ok"}

    def test_frontend_proxies_api_epics(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        _wait_for_http(HEALTH_ENDPOINT)
        epics_url = f"{FRONTEND_URL}/api/epics"
        assert _wait_for_http(epics_url), (
            f"API proxy not forwarding /api/epics at {epics_url}"
        )
        status, body = _http_get(epics_url)
        assert status == 200
        data = json.loads(body)
        assert "items" in data
        assert "total" in data
