import pytest
from datetime import date
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from personal_jira.app import create_app
from personal_jira.database import get_db


BASE_URL = "/api/v1/sprints"


class TestCreateSprintAPI:
    @pytest.mark.asyncio
    async def test_create_sprint(self, client: AsyncClient):
        payload = {
            "name": "Sprint 1",
            "goal": "Ship MVP",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        }
        resp = await client.post(BASE_URL, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Sprint 1"
        assert data["goal"] == "Ship MVP"
        assert data["status"] == "planning"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_sprint_minimal(self, client: AsyncClient):
        payload = {
            "name": "Sprint 2",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        }
        resp = await client.post(BASE_URL, json=payload)
        assert resp.status_code == 201
        assert resp.json()["goal"] is None

    @pytest.mark.asyncio
    async def test_create_sprint_missing_name(self, client: AsyncClient):
        payload = {
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        }
        resp = await client.post(BASE_URL, json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_sprint_end_before_start(self, client: AsyncClient):
        payload = {
            "name": "Bad Sprint",
            "start_date": "2026-04-06",
            "end_date": "2026-03-23",
        }
        resp = await client.post(BASE_URL, json=payload)
        assert resp.status_code == 422


class TestGetSprintAPI:
    @pytest.mark.asyncio
    async def test_get_sprint(self, client: AsyncClient):
        create_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = create_resp.json()["id"]

        resp = await client.get(f"{BASE_URL}/{sprint_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sprint_id

    @pytest.mark.asyncio
    async def test_get_sprint_not_found(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/{uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sprint_invalid_id(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/not-a-uuid")
        assert resp.status_code == 422


class TestListSprintsAPI:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        resp = await client.get(BASE_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_with_sprints(self, client: AsyncClient):
        for i in range(3):
            await client.post(BASE_URL, json={
                "name": f"Sprint {i}",
                "start_date": "2026-03-23",
                "end_date": "2026-04-06",
            })

        resp = await client.get(BASE_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_list_pagination(self, client: AsyncClient):
        for i in range(5):
            await client.post(BASE_URL, json={
                "name": f"Sprint {i}",
                "start_date": "2026-03-23",
                "end_date": "2026-04-06",
            })

        resp = await client.get(BASE_URL, params={"offset": 0, "limit": 2})
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_filter_status(self, client: AsyncClient):
        create_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = create_resp.json()["id"]
        await client.patch(f"{BASE_URL}/{sprint_id}", json={"status": "active"})

        await client.post(BASE_URL, json={
            "name": "Sprint 2",
            "start_date": "2026-04-06",
            "end_date": "2026-04-20",
        })

        resp = await client.get(BASE_URL, params={"status": "active"})
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Sprint 1"


class TestUpdateSprintAPI:
    @pytest.mark.asyncio
    async def test_update_sprint(self, client: AsyncClient):
        create_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = create_resp.json()["id"]

        resp = await client.patch(
            f"{BASE_URL}/{sprint_id}",
            json={"name": "Updated", "status": "active"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"
        assert resp.json()["status"] == "active"

    @pytest.mark.asyncio
    async def test_update_not_found(self, client: AsyncClient):
        resp = await client.patch(
            f"{BASE_URL}/{uuid4()}",
            json={"name": "X"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_empty_body(self, client: AsyncClient):
        create_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = create_resp.json()["id"]

        resp = await client.patch(f"{BASE_URL}/{sprint_id}", json={})
        assert resp.status_code == 200


class TestDeleteSprintAPI:
    @pytest.mark.asyncio
    async def test_delete_sprint(self, client: AsyncClient):
        create_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = create_resp.json()["id"]

        resp = await client.delete(f"{BASE_URL}/{sprint_id}")
        assert resp.status_code == 204

        get_resp = await client.get(f"{BASE_URL}/{sprint_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient):
        resp = await client.delete(f"{BASE_URL}/{uuid4()}")
        assert resp.status_code == 404


class TestSprintIssuesAPI:
    @pytest.mark.asyncio
    async def test_add_issue_to_sprint(self, client: AsyncClient):
        sprint_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = sprint_resp.json()["id"]

        issue_resp = await client.post("/api/v1/issues", json={
            "title": "Task 1",
        })
        issue_id = issue_resp.json()["id"]

        resp = await client.post(
            f"{BASE_URL}/{sprint_id}/issues",
            json={"issue_id": issue_id},
        )
        assert resp.status_code == 200
        assert resp.json()["sprint_id"] == sprint_id

    @pytest.mark.asyncio
    async def test_add_issue_sprint_not_found(self, client: AsyncClient):
        issue_resp = await client.post("/api/v1/issues", json={
            "title": "Task 1",
        })
        issue_id = issue_resp.json()["id"]

        resp = await client.post(
            f"{BASE_URL}/{uuid4()}/issues",
            json={"issue_id": issue_id},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_issue_from_sprint(self, client: AsyncClient):
        sprint_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = sprint_resp.json()["id"]

        issue_resp = await client.post("/api/v1/issues", json={
            "title": "Task 1",
        })
        issue_id = issue_resp.json()["id"]

        await client.post(
            f"{BASE_URL}/{sprint_id}/issues",
            json={"issue_id": issue_id},
        )

        resp = await client.delete(f"{BASE_URL}/{sprint_id}/issues/{issue_id}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_get_sprint_issues(self, client: AsyncClient):
        sprint_resp = await client.post(BASE_URL, json={
            "name": "Sprint 1",
            "start_date": "2026-03-23",
            "end_date": "2026-04-06",
        })
        sprint_id = sprint_resp.json()["id"]

        for i in range(3):
            issue_resp = await client.post("/api/v1/issues", json={
                "title": f"Task {i}",
            })
            await client.post(
                f"{BASE_URL}/{sprint_id}/issues",
                json={"issue_id": issue_resp.json()["id"]},
            )

        resp = await client.get(f"{BASE_URL}/{sprint_id}/issues")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    @pytest.mark.asyncio
    async def test_get_sprint_issues_not_found(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/{uuid4()}/issues")
        assert resp.status_code == 404
