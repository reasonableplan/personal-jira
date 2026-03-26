from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_import_app():
    """app.main에서 app을 import할 수 있는지 확인."""
    assert app is not None
    assert app.title == "Personal Jira"


def test_health_check():
    """/health 엔드포인트가 200과 정상 응답을 반환하는지 확인."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
