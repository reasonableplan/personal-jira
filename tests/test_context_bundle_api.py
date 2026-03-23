import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from personal_jira.api.v1.endpoints.context_bundle import router
from personal_jira.models.context_bundle import BundleItemType


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app: FastAPI) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )


class TestCreateBundle:
    @pytest.mark.asyncio
    async def test_create_bundle_201(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        payload = {
            "items": [
                {"item_type": "file", "path": "src/main.py"},
            ],
        }
        mock_bundle = MagicMock()
        mock_bundle.id = uuid.uuid4()
        mock_bundle.issue_id = issue_id
        mock_bundle.items = []
        mock_bundle.created_at = "2026-01-01T00:00:00Z"
        mock_bundle.updated_at = "2026-01-01T00:00:00Z"

        with patch(
            "personal_jira.api.v1.endpoints.context_bundle.context_bundle_service.create_bundle",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            resp = await client.post(
                f"/api/v1/issues/{issue_id}/bundles", json=payload
            )

        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_create_bundle_empty_items_422(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/issues/{issue_id}/bundles", json={"items": []}
        )
        assert resp.status_code == 422


class TestGetBundle:
    @pytest.mark.asyncio
    async def test_get_bundle_200(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        bundle_id = uuid.uuid4()
        mock_bundle = MagicMock()
        mock_bundle.id = bundle_id
        mock_bundle.issue_id = issue_id
        mock_bundle.items = []
        mock_bundle.created_at = "2026-01-01T00:00:00Z"
        mock_bundle.updated_at = "2026-01-01T00:00:00Z"

        with patch(
            "personal_jira.api.v1.endpoints.context_bundle.context_bundle_service.get_bundle",
            new_callable=AsyncMock,
            return_value=mock_bundle,
        ):
            resp = await client.get(
                f"/api/v1/issues/{issue_id}/bundles/{bundle_id}"
            )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_bundle_404(self, client: AsyncClient) -> None:
        from fastapi import HTTPException

        with patch(
            "personal_jira.api.v1.endpoints.context_bundle.context_bundle_service.get_bundle",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=404, detail="Bundle not found"),
        ):
            resp = await client.get(
                f"/api/v1/issues/{uuid.uuid4()}/bundles/{uuid.uuid4()}"
            )

        assert resp.status_code == 404


class TestListBundles:
    @pytest.mark.asyncio
    async def test_list_bundles_200(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        with patch(
            "personal_jira.api.v1.endpoints.context_bundle.context_bundle_service.list_bundles",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get(f"/api/v1/issues/{issue_id}/bundles")

        assert resp.status_code == 200
        assert resp.json() == []


class TestDeleteBundle:
    @pytest.mark.asyncio
    async def test_delete_bundle_204(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        bundle_id = uuid.uuid4()

        with patch(
            "personal_jira.api.v1.endpoints.context_bundle.context_bundle_service.delete_bundle",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await client.delete(
                f"/api/v1/issues/{issue_id}/bundles/{bundle_id}"
            )

        assert resp.status_code == 204


class TestInvalidUUID:
    @pytest.mark.asyncio
    async def test_invalid_issue_id_422(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/issues/not-a-uuid/bundles")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_bundle_id_422(self, client: AsyncClient) -> None:
        issue_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/issues/{issue_id}/bundles/not-a-uuid")
        assert resp.status_code == 422
