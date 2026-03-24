import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app


@pytest.fixture
def client(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


BASE_URL = "http://test/issues"


@pytest.mark.asyncio
async def test_create_issue(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/issues", json={"title": "New issue", "priority": "high"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "New issue"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_issue_validation_error(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/issues", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_issue(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/issues", json={"title": "Get me"})
        issue_id = create_resp.json()["id"]
        resp = await ac.get(f"/issues/{issue_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get me"


@pytest.mark.asyncio
async def test_get_issue_not_found(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/issues/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_issues(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/issues", json={"title": "A"})
        await ac.post("/issues", json={"title": "B"})
        resp = await ac.get("/issues")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_issues_with_filters(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/issues", json={"title": "High", "priority": "high"})
        await ac.post("/issues", json={"title": "Low", "priority": "low"})
        resp = await ac.get("/issues", params={"priority": "high"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "High"


@pytest.mark.asyncio
async def test_list_issues_pagination(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for i in range(5):
            await ac.post("/issues", json={"title": f"Issue {i}"})
        resp = await ac.get("/issues", params={"offset": 2, "limit": 2})
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


@pytest.mark.asyncio
async def test_update_issue(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/issues", json={"title": "Old"})
        issue_id = create_resp.json()["id"]
        resp = await ac.put(f"/issues/{issue_id}", json={"title": "New", "status": "done"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"
    assert resp.json()["status"] == "done"


@pytest.mark.asyncio
async def test_update_issue_not_found(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/issues/99999", json={"title": "Nope"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_issue(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_resp = await ac.post("/issues", json={"title": "Delete me"})
        issue_id = create_resp.json()["id"]
        resp = await ac.delete(f"/issues/{issue_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_issue_not_found(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/issues/99999")
    assert resp.status_code == 404
