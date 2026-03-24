import pytest
from httpx import AsyncClient

API_PREFIX = "/api/issues"


@pytest.mark.anyio
async def test_create_issue_minimal(client: AsyncClient) -> None:
    response = await client.post(API_PREFIX, json={"title": "Test issue"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test issue"
    assert data["description"] is None
    assert data["status"] == "todo"
    assert data["priority"] == 3
    assert "id" in data
    assert "created_at" in data


@pytest.mark.anyio
async def test_create_issue_full(client: AsyncClient) -> None:
    payload = {"title": "Full issue", "description": "A description", "priority": 1}
    response = await client.post(API_PREFIX, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Full issue"
    assert data["description"] == "A description"
    assert data["priority"] == 1


@pytest.mark.anyio
async def test_create_issue_missing_title(client: AsyncClient) -> None:
    response = await client.post(API_PREFIX, json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_issue_priority_out_of_range(client: AsyncClient) -> None:
    response = await client.post(API_PREFIX, json={"title": "Bad", "priority": 0})
    assert response.status_code == 422

    response = await client.post(API_PREFIX, json={"title": "Bad", "priority": 6})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_issue(client: AsyncClient) -> None:
    create = await client.post(API_PREFIX, json={"title": "To fetch"})
    issue_id = create.json()["id"]

    response = await client.get(f"{API_PREFIX}/{issue_id}")
    assert response.status_code == 200
    assert response.json()["id"] == issue_id
    assert response.json()["title"] == "To fetch"


@pytest.mark.anyio
async def test_get_issue_not_found(client: AsyncClient) -> None:
    response = await client.get(f"{API_PREFIX}/99999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_issues_empty(client: AsyncClient) -> None:
    response = await client.get(API_PREFIX)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.anyio
async def test_list_issues(client: AsyncClient) -> None:
    await client.post(API_PREFIX, json={"title": "Issue 1"})
    await client.post(API_PREFIX, json={"title": "Issue 2"})

    response = await client.get(API_PREFIX)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.anyio
async def test_update_issue(client: AsyncClient) -> None:
    create = await client.post(API_PREFIX, json={"title": "Original"})
    issue_id = create.json()["id"]

    response = await client.patch(
        f"{API_PREFIX}/{issue_id}", json={"title": "Updated", "description": "New desc"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "New desc"


@pytest.mark.anyio
async def test_update_issue_partial(client: AsyncClient) -> None:
    create = await client.post(
        API_PREFIX, json={"title": "Original", "description": "Keep me"}
    )
    issue_id = create.json()["id"]

    response = await client.patch(f"{API_PREFIX}/{issue_id}", json={"title": "Changed"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Changed"
    assert data["description"] == "Keep me"


@pytest.mark.anyio
async def test_delete_issue(client: AsyncClient) -> None:
    create = await client.post(API_PREFIX, json={"title": "To delete"})
    issue_id = create.json()["id"]

    response = await client.delete(f"{API_PREFIX}/{issue_id}")
    assert response.status_code == 204

    get_response = await client.get(f"{API_PREFIX}/{issue_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_update_status(client: AsyncClient) -> None:
    create = await client.post(API_PREFIX, json={"title": "Status test"})
    issue_id = create.json()["id"]

    response = await client.patch(
        f"{API_PREFIX}/{issue_id}/status", json={"status": "in_progress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.anyio
async def test_update_status_invalid(client: AsyncClient) -> None:
    create = await client.post(API_PREFIX, json={"title": "Bad status"})
    issue_id = create.json()["id"]

    response = await client.patch(
        f"{API_PREFIX}/{issue_id}/status", json={"status": "invalid_status"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_filter_by_status(client: AsyncClient) -> None:
    await client.post(API_PREFIX, json={"title": "Todo 1"})
    await client.post(API_PREFIX, json={"title": "Todo 2"})
    create3 = await client.post(API_PREFIX, json={"title": "Done 1"})
    await client.patch(
        f"{API_PREFIX}/{create3.json()['id']}/status", json={"status": "done"}
    )

    response = await client.get(API_PREFIX, params={"status": "todo"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["status"] == "todo" for item in data["items"])


@pytest.mark.anyio
async def test_filter_by_priority(client: AsyncClient) -> None:
    await client.post(API_PREFIX, json={"title": "P1", "priority": 1})
    await client.post(API_PREFIX, json={"title": "P1 again", "priority": 1})
    await client.post(API_PREFIX, json={"title": "P5", "priority": 5})

    response = await client.get(API_PREFIX, params={"priority": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["priority"] == 1 for item in data["items"])


@pytest.mark.anyio
async def test_filter_combined(client: AsyncClient) -> None:
    await client.post(API_PREFIX, json={"title": "Match", "priority": 2})
    await client.post(API_PREFIX, json={"title": "Wrong priority", "priority": 5})
    create3 = await client.post(API_PREFIX, json={"title": "Wrong status", "priority": 2})
    await client.patch(
        f"{API_PREFIX}/{create3.json()['id']}/status", json={"status": "done"}
    )

    response = await client.get(API_PREFIX, params={"status": "todo", "priority": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Match"
