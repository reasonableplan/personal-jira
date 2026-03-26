from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_import_app() -> None:
    """app.main에서 app을 import할 수 있는지 확인."""
    assert app is not None
    assert app.title == "Personal Jira"


def test_health_check() -> None:
    """/health 엔드포인트가 200과 정상 응답을 반환하는지 확인."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_endpoint() -> None:
    """/docs Swagger UI에 접근할 수 있는지 확인."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema() -> None:
    """OpenAPI 스키마가 올바른 title/version을 포함하는지 확인."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Personal Jira"
    assert schema["info"]["version"] == "0.1.0"


def test_cors_headers() -> None:
    """CORS preflight에서 프론트엔드 origin이 허용되는지 확인."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_routers_importable() -> None:
    """모든 라우터 모듈이 import 가능하고 올바른 prefix를 가지는지 확인."""
    from app.routers import dashboard, epics, labels, stories, tasks

    expected = {
        "epics": "/api/epics",
        "stories": "/api/stories",
        "tasks": "/api/tasks",
        "labels": "/api/labels",
        "dashboard": "/api/dashboard",
    }
    modules = {
        "epics": epics,
        "stories": stories,
        "tasks": tasks,
        "labels": labels,
        "dashboard": dashboard,
    }
    for name, prefix in expected.items():
        router = modules[name].router
        assert router.prefix == prefix, (
            f"Router '{name}' has prefix '{router.prefix}', expected '{prefix}'"
        )
