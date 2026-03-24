import pytest
from httpx import AsyncClient

from app.main import app


def test_app_exists() -> None:
    assert app is not None


def test_app_title() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    assert app.title == settings.APP_NAME


@pytest.mark.anyio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
