from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestBackendDockerfile:
    @pytest.fixture
    def content(self) -> str:
        return (ROOT / "backend" / "Dockerfile").read_text()

    def test_file_exists(self) -> None:
        assert (ROOT / "backend" / "Dockerfile").exists()

    def test_base_image(self, content: str) -> None:
        assert "python:3.12-slim" in content

    def test_uv_install(self, content: str) -> None:
        assert "uv" in content

    def test_uvicorn_cmd(self, content: str) -> None:
        assert "uvicorn" in content

    def test_port_exposed(self, content: str) -> None:
        assert "8000" in content

    def test_non_root_user(self, content: str) -> None:
        assert "appuser" in content or "USER" in content


class TestFrontendDockerfile:
    @pytest.fixture
    def content(self) -> str:
        return (ROOT / "frontend" / "Dockerfile").read_text()

    def test_file_exists(self) -> None:
        assert (ROOT / "frontend" / "Dockerfile").exists()

    def test_node_build_stage(self, content: str) -> None:
        assert "node:20-alpine" in content

    def test_nginx_stage(self, content: str) -> None:
        assert "nginx:alpine" in content

    def test_multi_stage(self, content: str) -> None:
        assert content.count("FROM") >= 2

    def test_port_exposed(self, content: str) -> None:
        assert "80" in content


class TestNginxConf:
    @pytest.fixture
    def content(self) -> str:
        return (ROOT / "frontend" / "nginx.conf").read_text()

    def test_file_exists(self) -> None:
        assert (ROOT / "frontend" / "nginx.conf").exists()

    def test_spa_fallback(self, content: str) -> None:
        assert "try_files" in content
        assert "index.html" in content

    def test_api_proxy(self, content: str) -> None:
        assert "proxy_pass" in content
        assert "backend" in content

    def test_listen_port(self, content: str) -> None:
        assert "listen" in content
        assert "80" in content
