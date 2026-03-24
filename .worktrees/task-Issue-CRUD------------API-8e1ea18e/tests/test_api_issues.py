import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue
from app.schemas.issue import IssueStatus


@pytest.fixture
async def sample_issue(db_session: AsyncSession) -> Issue:
    issue = Issue(title="Sample", description="desc", status="todo", priority=3)
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


@pytest.fixture
async def multiple_issues(db_session: AsyncSession) -> list[Issue]:
    issues = [
        Issue(title="A", status="todo", priority=1),
        Issue(title="B", status="in_progress", priority=2),
        Issue(title="C", status="done", priority=3),
        Issue(title="D", status="todo", priority=1),
    ]
    db_session.add_all(issues)
    await db_session.commit()
    for i in issues:
        await db_session.refresh(i)
    return issues


@pytest.mark.anyio
async def test_create_issue(client: AsyncClient) -> None:
    response = await client.post("/issues", json={"title": "New Issue", "priority": 2})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Issue"
    assert data["priority"] == 2
    assert data["status"] == "todo"
    assert data["id"] is not None
    assert data["created_at"] is not None


@pytest.mark.anyio
async def test_create_issue_minimal(client: AsyncClient) -> None:
    response = await client.post("/issues", json={"title": "Minimal"})
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None
    assert data["priority"] == 3


@pytest.mark.anyio
async def test_create_issue_validation_error(client: AsyncClient) -> None:
    response = await client.post("/issues", json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_issue(client: AsyncClient, sample_issue: Issue) -> None:
    response = await client.get(f"/issues/{sample_issue.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_issue.id
    assert data["title"] == "Sample"


@pytest.mark.anyio
async def test_get_issue_not_found(client: AsyncClient) -> None:
    response = await client.get("/issues/99999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_list_issues(client: AsyncClient, multiple_issues: list[Issue]) -> None:
    response = await client.get("/issues")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4


@pytest.mark.anyio
async def test_list_issues_filter_status(
    client: AsyncClient, multiple_issues: list[Issue]
) -> None:
    response = await client.get("/issues", params={"status": "todo"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(i["status"] == "todo" for i in data["items"])


@pytest.mark.anyio
async def test_list_issues_filter_priority(
    client: AsyncClient, multiple_issues: list[Issue]
) -> None:
    response = await client.get("/issues", params={"priority": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(i["priority"] == 1 for i in data["items"])


@pytest.mark.anyio
async def test_list_issues_filter_both(
    client: AsyncClient, multiple_issues: list[Issue]
) -> None:
    response = await client.get("/issues", params={"status": "todo", "priority": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.anyio
async def test_list_issues_empty(client: AsyncClient) -> None:
    response = await client.get("/issues")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.anyio
async def test_update_issue(client: AsyncClient, sample_issue: Issue) -> None:
    response = await client.put(
        f"/issues/{sample_issue.id}", json={"title": "Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "desc"
    assert data["updated_at"] is not None


@pytest.mark.anyio
async def test_update_issue_not_found(client: AsyncClient) -> None:
    response = await client.put("/issues/99999", json={"title": "X"})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_issue_partial(client: AsyncClient, sample_issue: Issue) -> None:
    response = await client.put(
        f"/issues/{sample_issue.id}", json={"priority": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == 5
    assert data["title"] == "Sample"


@pytest.mark.anyio
async def test_delete_issue(client: AsyncClient, sample_issue: Issue) -> None:
    response = await client.delete(f"/issues/{sample_issue.id}")
    assert response.status_code == 204
    response = await client.get(f"/issues/{sample_issue.id}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_issue_not_found(client: AsyncClient) -> None:
    response = await client.delete("/issues/99999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_status(
    client: AsyncClient, sample_issue: Issue
) -> None:
    response = await client.patch(
        f"/issues/{sample_issue.id}/status", json={"status": "done"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["updated_at"] is not None


@pytest.mark.anyio
async def test_update_status_not_found(client: AsyncClient) -> None:
    response = await client.patch(
        "/issues/99999/status", json={"status": "done"}
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_status_invalid(client: AsyncClient, sample_issue: Issue) -> None:
    response = await client.patch(
        f"/issues/{sample_issue.id}/status", json={"status": "invalid"}
    )
    assert response.status_code == 422
