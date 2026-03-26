"""커스텀 예외 클래스 및 에러 핸들러 테스트."""

from app.core.error_handlers import register_error_handlers
from app.core.exceptions import AppError, ConflictError, NotFoundError, ValidationError
from fastapi import FastAPI
from fastapi.testclient import TestClient

# --- 예외 클래스 단위 테스트 ---


def test_not_found_error_defaults() -> None:
    exc = NotFoundError()
    assert exc.detail == "Resource not found"
    assert exc.error_code == "NOT_FOUND"
    assert str(exc) == "Resource not found"


def test_not_found_error_custom() -> None:
    exc = NotFoundError(detail="Epic not found", error_code="EPIC_NOT_FOUND")
    assert exc.detail == "Epic not found"
    assert exc.error_code == "EPIC_NOT_FOUND"


def test_conflict_error_defaults() -> None:
    exc = ConflictError()
    assert exc.detail == "Resource conflict"
    assert exc.error_code == "CONFLICT"


def test_conflict_error_custom() -> None:
    exc = ConflictError(detail="Label already exists", error_code="LABEL_DUPLICATE")
    assert exc.detail == "Label already exists"
    assert exc.error_code == "LABEL_DUPLICATE"


def test_validation_error_defaults() -> None:
    exc = ValidationError()
    assert exc.detail == "Validation failed"
    assert exc.error_code == "VALIDATION_ERROR"


def test_validation_error_custom() -> None:
    exc = ValidationError(detail="Invalid status", error_code="INVALID_STATUS")
    assert exc.detail == "Invalid status"
    assert exc.error_code == "INVALID_STATUS"


def test_all_exceptions_inherit_from_app_error() -> None:
    assert issubclass(NotFoundError, AppError)
    assert issubclass(ConflictError, AppError)
    assert issubclass(ValidationError, AppError)


def test_app_error_inherits_from_exception() -> None:
    assert issubclass(AppError, Exception)


# --- 에러 핸들러 통합 테스트 ---


def _create_test_app() -> FastAPI:
    """테스트용 FastAPI 앱을 생성하고 에러 핸들러를 등록한다."""
    test_app = FastAPI()
    register_error_handlers(test_app)

    @test_app.get("/raise-not-found")
    async def raise_not_found() -> None:
        raise NotFoundError(detail="Task not found", error_code="TASK_NOT_FOUND")

    @test_app.get("/raise-conflict")
    async def raise_conflict() -> None:
        raise ConflictError(detail="Label already exists", error_code="LABEL_DUPLICATE")

    @test_app.get("/raise-validation")
    async def raise_validation() -> None:
        raise ValidationError(detail="Invalid status value", error_code="INVALID_STATUS")

    @test_app.get("/raise-not-found-default")
    async def raise_not_found_default() -> None:
        raise NotFoundError()

    return test_app


_test_app = _create_test_app()
client = TestClient(_test_app)


def test_not_found_handler_returns_404() -> None:
    response = client.get("/raise-not-found")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Task not found"
    assert body["error_code"] == "TASK_NOT_FOUND"


def test_conflict_handler_returns_409() -> None:
    response = client.get("/raise-conflict")
    assert response.status_code == 409
    body = response.json()
    assert body["detail"] == "Label already exists"
    assert body["error_code"] == "LABEL_DUPLICATE"


def test_validation_handler_returns_400() -> None:
    response = client.get("/raise-validation")
    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Invalid status value"
    assert body["error_code"] == "INVALID_STATUS"


def test_error_response_format_consistent() -> None:
    """모든 에러 응답이 {detail, error_code} 형식인지 확인."""
    for path in ("/raise-not-found", "/raise-conflict", "/raise-validation"):
        response = client.get(path)
        body = response.json()
        assert "detail" in body, f"Missing 'detail' in {path}"
        assert "error_code" in body, f"Missing 'error_code' in {path}"
        assert len(body) == 2, f"Unexpected fields in {path}: {body}"


def test_not_found_default_values_in_response() -> None:
    response = client.get("/raise-not-found-default")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Resource not found"
    assert body["error_code"] == "NOT_FOUND"


def test_error_handlers_registered_in_main_app() -> None:
    """main.py의 app에 에러 핸들러가 등록되어 있는지 확인."""
    from app.main import app

    assert NotFoundError in app.exception_handlers
    assert ConflictError in app.exception_handlers
    assert ValidationError in app.exception_handlers
