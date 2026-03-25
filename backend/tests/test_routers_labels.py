from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestCreateLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_create_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_label = MagicMock()
        mock_label.id = "label-1"
        mock_label.name = "bug"
        mock_label.color = "#FF0000"
        mock_svc.get_by_name = AsyncMock(return_value=None)
        mock_svc.create = AsyncMock(return_value=mock_label)
        resp = await client.post(
            "/api/labels", json={"name": "bug", "color": "#FF0000"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "bug"
        assert data["color"] == "#FF0000"

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_create_duplicate_name(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        existing = MagicMock()
        existing.id = "label-1"
        existing.name = "bug"
        mock_svc.get_by_name = AsyncMock(return_value=existing)
        resp = await client.post(
            "/api/labels", json={"name": "bug", "color": "#FF0000"}
        )
        assert resp.status_code == 409

    @pytest.mark.anyio
    async def test_create_invalid_color(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/labels", json={"name": "bug", "color": "red"}
        )
        assert resp.status_code == 422


class TestListLabels:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_list_all(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        label1 = MagicMock()
        label1.id = "l1"
        label1.name = "bug"
        label1.color = "#FF0000"
        label2 = MagicMock()
        label2.id = "l2"
        label2.name = "feature"
        label2.color = "#00FF00"
        mock_svc.list_all = AsyncMock(return_value=[label1, label2])
        resp = await client.get("/api/labels")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2


class TestUpdateLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        updated = MagicMock()
        updated.id = "l1"
        updated.name = "bugfix"
        updated.color = "#0000FF"
        mock_svc.get_by_name = AsyncMock(return_value=None)
        mock_svc.update = AsyncMock(return_value=updated)
        resp = await client.patch(
            "/api/labels/l1", json={"name": "bugfix"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "bugfix"

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_not_found(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.get_by_name = AsyncMock(return_value=None)
        mock_svc.update = AsyncMock(return_value=None)
        resp = await client.patch(
            "/api/labels/nonexistent", json={"name": "x"}
        )
        assert resp.status_code == 404

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_duplicate_name(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        existing = MagicMock()
        existing.id = "l2"
        existing.name = "feature"
        mock_svc.get_by_name = AsyncMock(return_value=existing)
        resp = await client.patch(
            "/api/labels/l1", json={"name": "feature"}
        )
        assert resp.status_code == 409


class TestDeleteLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_delete_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.delete = AsyncMock(return_value=True)
        resp = await client.delete("/api/labels/l1")
        assert resp.status_code == 204

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_delete_not_found(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.delete = AsyncMock(return_value=False)
        resp = await client.delete("/api/labels/nonexistent")
        assert resp.status_code == 404


class TestAttachLabelsToTask:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_attach_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        await self._setup_attach(mock_svc, task_exists=True)
        resp = await client.post(
            "/api/tasks/t1/labels", json={"label_ids": ["l1", "l2"]}
        )
        assert resp.status_code == 200
        assert resp.json() == ["l1", "l2"]

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_attach_task_not_found(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        await self._setup_attach(mock_svc, task_exists=False)
        resp = await client.post(
            "/api/tasks/t1/labels", json={"label_ids": ["l1"]}
        )
        assert resp.status_code == 404

    @staticmethod
    async def _setup_attach(
        mock_svc: MagicMock, *, task_exists: bool
    ) -> list[str]:
        from unittest.mock import AsyncMock
        from unittest.mock import MagicMock as MM

        mock_session_result = MM()
        if task_exists:
            mock_task = MM()
            mock_task.id = "t1"
            mock_session_result.scalar_one_or_none.return_value = mock_task
            mock_svc.attach_labels_to_task = AsyncMock(
                return_value=["l1", "l2"]
            )
        else:
            mock_session_result.scalar_one_or_none.return_value = None
        return ["l1", "l2"]


class TestDetachLabelFromTask:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_detach_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.detach_label_from_task = AsyncMock(return_value=True)
        resp = await client.delete("/api/tasks/t1/labels/l1")
        assert resp.status_code == 204

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_detach_not_found(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.detach_label_from_task = AsyncMock(return_value=False)
        resp = await client.delete("/api/tasks/t1/labels/nonexistent")
        assert resp.status_code == 404
