from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self) -> None:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_health_content_type(self) -> None:
        resp = client.get("/api/health")
        assert resp.headers["content-type"] == "application/json"
