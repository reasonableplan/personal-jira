import pytest
from app.core.exceptions import (
    AlreadyExistsError,
    AppException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    register_exception_handlers,
)
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _create_test_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/not-found")
    async def _raise_not_found() -> None:
        raise NotFoundError("User not found")

    @test_app.get("/already-exists")
    async def _raise_already_exists() -> None:
        raise AlreadyExistsError("User already exists")

    @test_app.get("/unauthorized")
    async def _raise_unauthorized() -> None:
        raise UnauthorizedError("Invalid credentials")

    @test_app.get("/forbidden")
    async def _raise_forbidden() -> None:
        raise ForbiddenError("Access denied")

    @test_app.get("/generic-app-error")
    async def _raise_generic() -> None:
        raise AppException("Something went wrong")

    @test_app.get("/unhandled")
    async def _raise_unhandled() -> None:
        raise RuntimeError("unexpected")

    return test_app


def test_app_exception_defaults() -> None:
    exc = AppException("test")
    assert exc.message == "test"
    assert exc.status_code == 500


def test_not_found_error_status_code() -> None:
    exc = NotFoundError("missing")
    assert exc.status_code == 404
    assert exc.message == "missing"


def test_already_exists_error_status_code() -> None:
    exc = AlreadyExistsError("duplicate")
    assert exc.status_code == 409


def test_unauthorized_error_status_code() -> None:
    exc = UnauthorizedError("no auth")
    assert exc.status_code == 401


def test_forbidden_error_status_code() -> None:
    exc = ForbiddenError("denied")
    assert exc.status_code == 403


@pytest.mark.asyncio
async def test_not_found_handler_returns_404() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/not-found")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_already_exists_handler_returns_409() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/already-exists")
    assert resp.status_code == 409
    assert resp.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_unauthorized_handler_returns_401() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/unauthorized")
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid credentials"}


@pytest.mark.asyncio
async def test_forbidden_handler_returns_403() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/forbidden")
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Access denied"}


@pytest.mark.asyncio
async def test_generic_app_exception_returns_500() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/generic-app-error")
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Something went wrong"}


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500() -> None:
    app = _create_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/unhandled")
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}


@pytest.mark.asyncio
async def test_validation_error_returns_422() -> None:
    app = _create_test_app()

    @app.get("/validate/{item_id}")
    async def _validate(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/validate/not-a-number")
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
