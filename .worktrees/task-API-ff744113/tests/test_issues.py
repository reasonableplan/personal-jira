from datetime import datetime

import pytest
from httpx import AsyncClient

ISSUES_URL = "/issues"


def _issue_url(issue_id: int) -> str:
    return f"{ISSUES_URL}/{issue_id}"


async def _create_issue(
    client: AsyncClient,
    title: str = "Test issue",
    description: str | None = None,
    priority: str = "medium",
) -> dict:
    payload: dict = {"title": title, "priority": priority}
    if description is not None:
        payload["description"] = description
    resp = await client.post(ISSUES_URL, json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_issue_success(client: AsyncClient) -> None:
    data = await _create_issue(client, title="New bug")
    assert data["id"] is not None
    assert data["title"] == "New bug"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["description"] is None
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_issue_validation_error_missing_title(client: AsyncClient) -> None:
    resp = await client.post(ISSUES_URL, json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_issue_success(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Fetch me")
    resp = await client.get(_issue_url(created["id"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Fetch me"


@pytest.mark.asyncio
async def test_get_issue_not_found(client: AsyncClient) -> None:
    resp = await client.get(_issue_url(99999))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_issues_empty(client: AsyncClient) -> None:
    resp = await client.get(ISSUES_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_issues_multiple(client: AsyncClient) -> None:
    await _create_issue(client, title="Issue 1")
    await _create_issue(client, title="Issue 2")
    await _create_issue(client, title="Issue 3")
    resp = await client.get(ISSUES_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_issues_filter_by_status(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Status filter test")
    await client.patch(
        f"{_issue_url(created['id'])}/status",
        json={"status": "in_progress"},
    )
    resp = await client.get(ISSUES_URL, params={"status": "in_progress"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(i["status"] == "in_progress" for i in data["items"])

    resp_todo = await client.get(ISSUES_URL, params={"status": "todo"})
    todo_ids = [i["id"] for i in resp_todo.json()["items"]]
    assert created["id"] not in todo_ids


@pytest.mark.asyncio
async def test_list_issues_filter_by_priority(client: AsyncClient) -> None:
    await _create_issue(client, title="High prio", priority="high")
    await _create_issue(client, title="Low prio", priority="low")
    resp = await client.get(ISSUES_URL, params={"priority": "high"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(i["priority"] == "high" for i in data["items"])


@pytest.mark.asyncio
async def test_update_issue_success(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Original")
    resp = await client.put(
        _issue_url(created["id"]),
        json={"title": "Updated", "description": "New desc", "priority": "critical"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated"
    assert data["description"] == "New desc"
    assert data["priority"] == "critical"


@pytest.mark.asyncio
async def test_update_issue_partial(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Partial", priority="low")
    resp = await client.put(
        _issue_url(created["id"]),
        json={"title": "Partial Updated"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Partial Updated"
    assert data["priority"] == "low"


@pytest.mark.asyncio
async def test_delete_issue_success(client: AsyncClient) -> None:
    created = await _create_issue(client, title="To delete")
    resp = await client.delete(_issue_url(created["id"]))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_issue_then_get_returns_404(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Delete and refetch")
    await client.delete(_issue_url(created["id"]))
    resp = await client.get(_issue_url(created["id"]))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_status_success(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Status change")
    assert created["status"] == "todo"
    resp = await client.patch(
        f"{_issue_url(created['id'])}/status",
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_patch_status_updates_updated_at(client: AsyncClient) -> None:
    created = await _create_issue(client, title="Timestamp check")
    original_updated = created["updated_at"]
    resp = await client.patch(
        f"{_issue_url(created['id'])}/status",
        json={"status": "done"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["updated_at"] >= original_updated
    assert data["status"] == "done"
