from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.database import get_session
from app.main import app
from app.models.issue import Label
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def override_session(mock_session: AsyncMock):
    async def _override():
        yield mock_session

    app.dependency_overrides[get_session] = _override
    yield mock_session
    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_session: AsyncMock) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestCreateLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_create_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.get_by_name = AsyncMock(return_value=None)
        fake = Label(id="uuid1", name="bug", color="#FF0000")
        mock_svc.create = AsyncMock(return_value=fake)
        resp = await client.post("/api/labels", json={"name": "bug", "color": "#FF0000"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "bug"
        assert data["color"] == "#FF0000"

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_create_duplicate_name(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        existing = Label(id="uuid1", name="bug", color="#FF0000")
        mock_svc.get_by_name = AsyncMock(return_value=existing)
        resp = await client.post("/api/labels", json={"name": "bug", "color": "#00FF00"})
        assert resp.status_code == 409

    @pytest.mark.anyio
    async def test_create_invalid_color(self, client: AsyncClient) -> None:
        resp = await client.post("/api/labels", json={"name": "bug", "color": "red"})
        assert resp.status_code == 422


class TestListLabels:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_list_all(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        fake1 = Label(id="1", name="bug", color="#FF0000")
        fake2 = Label(id="2", name="feature", color="#00FF00")
        mock_svc.list_all = AsyncMock(return_value=[fake1, fake2])
        resp = await client.get("/api/labels")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_list_empty(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.list_all = AsyncMock(return_value=[])
        resp = await client.get("/api/labels")
        assert resp.status_code == 200
        assert resp.json() == []


class TestUpdateLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        updated = Label(id="uuid1", name="bugfix", color="#FF0000")
        mock_svc.get_by_name = AsyncMock(return_value=None)
        mock_svc.update = AsyncMock(return_value=updated)
        resp = await client.patch("/api/labels/uuid1", json={"name": "bugfix"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "bugfix"

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_not_found(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.get_by_name = AsyncMock(return_value=None)
        mock_svc.update = AsyncMock(return_value=None)
        resp = await client.patch("/api/labels/nonexistent", json={"name": "x"})
        assert resp.status_code == 404

    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_update_duplicate_name(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        existing = Label(id="other-id", name="taken", color="#000000")
        mock_svc.get_by_name = AsyncMock(return_value=existing)
        resp = await client.patch("/api/labels/uuid1", json={"name": "taken"})
        assert resp.status_code == 409


class TestDeleteLabel:
    @pytest.mark.anyio
    @patch("app.routers.labels.label_service")
    async def test_delete_success(
        self, mock_svc: MagicMock, client: AsyncClient
    ) -> None:
        mock_svc.delete = AsyncMock(return_value=True)
        resp = await client.delete("/api/labels/uuid1")
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
        self, mock_svc: MagicMock, client: AsyncClient, override_session: AsyncMock
    ) -> None:
        from app.models.issue import Task

        MagicMock()
        task_result = MagicMock()
        task_result.scalar_one_or_none.return_value = Task(
            id="t1", story_id="s1", title="task"
        )
        override_session.execute.return_value = task_result
        mock_svc.attach_labels_to_task = AsyncMock(return_value=["l1", "l2"])
        resp = await client.post(
            "/api/tasks/t1/labels", json={"label_ids": ["l1", "l2"]}
        )
        assert resp.status_code == 200
        assert resp.json() == ["l1", "l2"]

    @pytest.mark.anyio
    async def test_attach_task_not_found(
        self, client: AsyncClient, override_session: AsyncMock
    ) -> None:
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        override_session.execute.return_value = result_mock
        resp = await client.post(
            "/api/tasks/nonexistent/labels", json={"label_ids": ["l1"]}
        )
        assert resp.status_code == 404


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
