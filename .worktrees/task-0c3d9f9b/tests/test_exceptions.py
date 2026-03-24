import pytest
from httpx import ASGITransport, AsyncClient

from app.exceptions import (
    AppException,
    IssueNotFoundException,
)
from app.schemas.error import ErrorResponse


def test_app_exception_defaults():
    exc = AppException(detail="something failed")
    assert exc.detail == "something failed"
    assert exc.status_code == 500


def test_app_exception_custom_status():
    exc = AppException(detail="bad", status_code=400)
    assert exc.status_code == 400


def test_issue_not_found_exception():
    exc = IssueNotFoundException(issue_id=42)
    assert exc.status_code == 404
    assert "42" in exc.detail


def test_error_response_schema():
    resp = ErrorResponse(detail="not found", status_code=404)
    assert resp.detail == "not found"
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_app_exception_handler():
    from app.main import app

    @app.get("/test-app-exception")
    async def _raise_app_exc() -> None:
        raise AppException(detail="custom error", status_code=418)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test-app-exception")
    assert response.status_code == 418
    body = response.json()
    assert body["detail"] == "custom error"
    assert body["status_code"] == 418


@pytest.mark.asyncio
async def test_issue_not_found_handler():
    from app.main import app

    @app.get("/test-issue-not-found")
    async def _raise_not_found() -> None:
        raise IssueNotFoundException(issue_id=99)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test-issue-not-found")
    assert response.status_code == 404
    body = response.json()
    assert "99" in body["detail"]
    assert body["status_code"] == 404


@pytest.mark.asyncio
async def test_validation_error_handler():
    from app.main import app
    from app.schemas.issue import IssueCreate

    @app.post("/test-validation")
    async def _validate(payload: IssueCreate) -> dict[str, str]:
        return {"title": payload.title}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/test-validation", json={})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert body["status_code"] == 422


@pytest.mark.asyncio
async def test_unhandled_exception_handler():
    from app.main import app

    @app.get("/test-unhandled")
    async def _raise_unhandled() -> None:
        raise RuntimeError("unexpected")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test-unhandled")
    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error"
    assert body["status_code"] == 500


@pytest.mark.asyncio
async def test_404_not_found_handler():
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/nonexistent-route")
    assert response.status_code == 404
    body = response.json()
    assert body["status_code"] == 404
