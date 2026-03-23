import uuid
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from personal_jira.app import create_app
from personal_jira.models.sprint import Sprint, SprintStatus

app = create_app()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
async def client(mock_db):
    async def override_get_db():
        yield mock_db

    from personal_jira.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


class TestCreateSprintEndpoint:
    @pytest.mark.asyncio
    async def test_create_sprint_201(self, client: AsyncClient) -> None:
        payload = {
            "name": "Sprint 1",
            "goal": "Complete MVP",
            "start_date": "2026-03-01",
            "end_date": "2026-03-14",
        }
        with patch("personal_jira.api.sprint.sprint_service.create", new_callable=AsyncMock) as mock_create:
            sprint_id = uuid.uuid4()
            mock_create.return_value = Sprint(
                id=sprint_id,
                name="Sprint 1",
                goal="Complete MVP",
                status=SprintStatus.PLANNING,
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 14),
            )
            resp = await client.post("/api/v1/sprints", json=payload)

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Sprint 1"
        assert data["status"] == "planning"

    @pytest.mark.asyncio
    async def test_create_sprint_422_missing_name(self, client: AsyncClient) -> None:
        payload = {
            "start_date": "2026-03-01",
            "end_date": "2026-03-14",
        }
        resp = await client.post("/api/v1/sprints", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_sprint_422_end_before_start(self, client: AsyncClient) -> None:
        payload = {
            "name": "Sprint 1",
            "start_date": "2026-03-14",
            "end_date": "2026-03-01",
        }
        resp = await client.post("/api/v1/sprints", json=payload)
        assert resp.status_code == 422


class TestGetSprintEndpoint:
    @pytest.mark.asyncio
    async def test_get_sprint_200(self, client: AsyncClient) -> None:
        sprint_id = uuid.uuid4()
        with patch("personal_jira.api.sprint.sprint_service.get_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = Sprint(
                id=sprint_id,
                name="Sprint 1",
                status=SprintStatus.ACTIVE,
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 14),
            )
            resp = await client.get(f"/api/v1/sprints/{sprint_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == str(sprint_id)

    @pytest.mark.asyncio
    async def test_get_sprint_404(self, client: AsyncClient) -> None:
        with patch("personal_jira.api.sprint.sprint_service.get_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            resp = await client.get(f"/api/v1/sprints/{uuid.uuid4()}")

        assert resp.status_code == 404


class TestListSprintsEndpoint:
    @pytest.mark.asyncio
    async def test_list_sprints_200(self, client: AsyncClient) -> None:
        with patch("personal_jira.api.sprint.sprint_service.list_all", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [
                Sprint(name="S1", start_date=date(2026, 3, 1), end_date=date(2026, 3, 14)),
                Sprint(name="S2", start_date=date(2026, 3, 15), end_date=date(2026, 3, 28)),
            ]
            resp = await client.get("/api/v1/sprints")

        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestUpdateSprintEndpoint:
    @pytest.mark.asyncio
    async def test_update_sprint_200(self, client: AsyncClient) -> None:
        sprint_id = uuid.uuid4()
        with patch("personal_jira.api.sprint.sprint_service.update", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = Sprint(
                id=sprint_id,
                name="Updated Sprint",
                status=SprintStatus.ACTIVE,
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 14),
            )
            resp = await client.patch(f"/api/v1/sprints/{sprint_id}", json={"name": "Updated Sprint"})

        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Sprint"

    @pytest.mark.asyncio
    async def test_update_sprint_404(self, client: AsyncClient) -> None:
        with patch("personal_jira.api.sprint.sprint_service.update", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = None
            resp = await client.patch(f"/api/v1/sprints/{uuid.uuid4()}", json={"name": "X"})

        assert resp.status_code == 404


class TestDeleteSprintEndpoint:
    @pytest.mark.asyncio
    async def test_delete_sprint_204(self, client: AsyncClient) -> None:
        sprint_id = uuid.uuid4()
        with patch("personal_jira.api.sprint.sprint_service.delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            resp = await client.delete(f"/api/v1/sprints/{sprint_id}")

        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_sprint_404(self, client: AsyncClient) -> None:
        with patch("personal_jira.api.sprint.sprint_service.delete", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = False
            resp = await client.delete(f"/api/v1/sprints/{uuid.uuid4()}")

        assert resp.status_code == 404
