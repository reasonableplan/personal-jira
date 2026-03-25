import pytest
from app.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
    register_exception_handlers,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def exception_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    async def raise_not_found() -> None:
        raise NotFoundError("Item not found")

    @app.get("/conflict")
    async def raise_conflict() -> None:
        raise ConflictError("Already exists")

    @app.get("/validation")
    async def raise_validation() -> None:
        raise ValidationError("Invalid input")

    return app


@pytest.fixture
def exception_client(exception_app: FastAPI) -> TestClient:
    return TestClient(exception_app)


class TestNotFoundError:
    def test_returns_404(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/not-found")
        assert resp.status_code == 404

    def test_returns_detail(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/not-found")
        assert resp.json() == {"detail": "Item not found"}


class TestConflictError:
    def test_returns_409(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/conflict")
        assert resp.status_code == 409

    def test_returns_detail(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/conflict")
        assert resp.json() == {"detail": "Already exists"}


class TestValidationError:
    def test_returns_422(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/validation")
        assert resp.status_code == 422

    def test_returns_detail(self, exception_client: TestClient) -> None:
        resp = exception_client.get("/validation")
        assert resp.json() == {"detail": "Invalid input"}


class TestExceptionClasses:
    def test_not_found_message(self) -> None:
        err = NotFoundError("test")
        assert str(err) == "test"

    def test_conflict_message(self) -> None:
        err = ConflictError("test")
        assert str(err) == "test"

    def test_validation_message(self) -> None:
        err = ValidationError("test")
        assert str(err) == "test"
