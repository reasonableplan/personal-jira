import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, Field

from app.core.exceptions import (
    AppException,
    IssueNotFoundException,
    handle_app_exception,
    handle_generic_exception,
    handle_validation_exception,
    register_exception_handlers,
)


def test_app_exception_defaults() -> None:
    exc = AppException(detail="fail")
    assert exc.detail == "fail"
    assert exc.status_code == 400


def test_app_exception_custom_status() -> None:
    exc = AppException(detail="not found", status_code=404)
    assert exc.status_code == 404


def test_issue_not_found_exception() -> None:
    exc = IssueNotFoundException(issue_id=42)
    assert exc.status_code == 404
    assert "42" in exc.detail


def _create_test_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    class Body(BaseModel):
        value: int = Field(ge=1)

    @test_app.get("/app-error")
    async def app_error() -> None:
        raise AppException(detail="custom error", status_code=409)

    @test_app.get("/not-found")
    async def not_found() -> None:
        raise IssueNotFoundException(issue_id=1)

    @test_app.post("/validate")
    async def validate(body: Body) -> dict:
        return {"value": body.value}

    @test_app.get("/unexpected")
    async def unexpected() -> None:
        raise RuntimeError("boom")

    return test_app


@pytest.fixture
async def test_client() -> AsyncClient:
    transport = ASGITransport(app=_create_test_app())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_app_exception_response(test_client: AsyncClient) -> None:
    resp = await test_client.get("/app-error")
    assert resp.status_code == 409
    body = resp.json()
    assert body["detail"] == "custom error"
    assert body["status_code"] == 409


@pytest.mark.anyio
async def test_issue_not_found_response(test_client: AsyncClient) -> None:
    resp = await test_client.get("/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body["status_code"] == 404
    assert "1" in body["detail"]


@pytest.mark.anyio
async def test_validation_error_response(test_client: AsyncClient) -> None:
    resp = await test_client.post("/validate", json={"value": -1})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status_code"] == 422
    assert "detail" in body


@pytest.mark.anyio
async def test_unexpected_error_response(test_client: AsyncClient) -> None:
    resp = await test_client.get("/unexpected")
    assert resp.status_code == 500
    body = resp.json()
    assert body["status_code"] == 500
    assert body["detail"] == "Internal server error"


@pytest.mark.anyio
async def test_error_response_format_consistency(test_client: AsyncClient) -> None:
    for path in ["/app-error", "/not-found", "/unexpected"]:
        resp = await test_client.get(path)
        body = resp.json()
        assert set(body.keys()) == {"detail", "status_code"}
