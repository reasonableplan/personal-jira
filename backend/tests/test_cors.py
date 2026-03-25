from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestCORS:
    def test_cors_allowed_origin(self) -> None:
        resp = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_allows_all_methods(self) -> None:
        resp = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        allowed = resp.headers.get("access-control-allow-methods", "")
        assert "POST" in allowed or "*" in allowed

    def test_cors_allows_all_headers(self) -> None:
        resp = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        allowed = resp.headers.get("access-control-allow-headers", "")
        assert "content-type" in allowed.lower() or "*" in allowed

    def test_cors_disallowed_origin(self) -> None:
        resp = client.options(
            "/api/health",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") != "http://evil.com"
