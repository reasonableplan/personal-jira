import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5434
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/api/health"
PROXY_HEALTH_ENDPOINT = f"{FRONTEND_URL}/api/health"
STARTUP_TIMEOUT = 120
POLL_INTERVAL = 2


def _is_docker_compose_running() -> bool:
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=10,
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _wait_for_tcp(host: str, port: int, timeout: int = STARTUP_TIMEOUT) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except (TimeoutError, ConnectionRefusedError, OSError):
            time.sleep(POLL_INTERVAL)
    return False


def _wait_for_http(url: str, timeout: int = STARTUP_TIMEOUT, expected_status: int = 200) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == expected_status:
                    return True
        except (urllib.error.URLError, OSError, ConnectionResetError):
            pass
        time.sleep(POLL_INTERVAL)
    return False


def _http_get(url: str, timeout: int = 10) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, body


@pytest.fixture(scope="module")
def docker_compose_up():
    if _is_docker_compose_running():
        yield
        return

    result = subprocess.run(
        ["docker", "compose", "up", "--build", "-d"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=300,
    )
    if result.returncode != 0:
        pytest.fail(f"docker compose up failed: {result.stderr}")

    yield

    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=60,
    )


class TestPostgresConnection:
    def test_postgres_port_open(self, docker_compose_up: None) -> None:
        assert _wait_for_tcp(POSTGRES_HOST, POSTGRES_PORT), (
            f"PostgreSQL not reachable on {POSTGRES_HOST}:{POSTGRES_PORT}"
        )

    def test_postgres_accepts_connections(self, docker_compose_up: None) -> None:
        _wait_for_tcp(POSTGRES_HOST, POSTGRES_PORT)
        try:
            result = subprocess.run(
                [
                    "docker", "compose", "exec", "-T", "db",
                    "pg_isready", "-U", "personal_jira", "-d", "personal_jira",
                ],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                timeout=15,
            )
            assert result.returncode == 0, f"pg_isready failed: {result.stderr}"
        except FileNotFoundError:
            pytest.skip("docker CLI not available")


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
    def test_frontend_serves_html(self, docker_compose_up: None) -> None:
        assert _wait_for_http(FRONTEND_URL), (
            f"Frontend not responding at {FRONTEND_URL}"
        )
        status, body = _http_get(FRONTEND_URL)
        assert status == 200
        assert "<!doctype html>" in body.lower() or "<html" in body.lower()

    def test_frontend_serves_react_app(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        status, body = _http_get(FRONTEND_URL)
        assert "<div id=\"root\"></div>" in body or 'id="root"' in body


class TestApiProxy:
    def test_proxy_forwards_api_health(self, docker_compose_up: None) -> None:
        _wait_for_http(FRONTEND_URL)
        _wait_for_http(HEALTH_ENDPOINT)
        assert _wait_for_http(PROXY_HEALTH_ENDPOINT), (
            f"API proxy not working at {PROXY_HEALTH_ENDPOINT}"
        )
        status, body = _http_get(PROXY_HEALTH_ENDPOINT)
        assert status == 200
        data = json.loads(body)
        assert data == {"status": "ok"}

    def test_proxy_preserves_json_content_type(self, docker_compose_up: None) -> None:
        _wait_for_http(PROXY_HEALTH_ENDPOINT)
        req = urllib.request.Request(PROXY_HEALTH_ENDPOINT, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("content-type", "")
            assert "application/json" in content_type
