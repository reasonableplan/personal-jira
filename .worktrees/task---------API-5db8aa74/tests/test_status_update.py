import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Issue
from app.schemas.issue import IssueStatus, StatusUpdate
from app.services.issue_service import update_issue_status


def test_status_update_schema_valid():
    schema = StatusUpdate(status=IssueStatus.IN_PROGRESS)
    assert schema.status == IssueStatus.IN_PROGRESS


def test_status_update_schema_all_statuses():
    for s in IssueStatus:
        schema = StatusUpdate(status=s)
        assert schema.status == s


def test_status_update_schema_requires_status():
    with pytest.raises(ValidationError):
        StatusUpdate()


def test_status_update_schema_rejects_invalid():
    with pytest.raises(ValidationError):
        StatusUpdate(status="invalid")


@pytest.mark.asyncio
async def test_update_issue_status_todo_to_in_progress(db_session: AsyncSession):
    issue = Issue(title="Test", status="todo")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    updated = await update_issue_status(db_session, issue.id, status="in_progress")
    assert updated.status == "in_progress"


@pytest.mark.asyncio
async def test_update_issue_status_to_done(db_session: AsyncSession):
    issue = Issue(title="Test", status="in_progress")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    updated = await update_issue_status(db_session, issue.id, status="done")
    assert updated.status == "done"


@pytest.mark.asyncio
async def test_update_issue_status_done_to_todo(db_session: AsyncSession):
    issue = Issue(title="Test", status="done")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    updated = await update_issue_status(db_session, issue.id, status="todo")
    assert updated.status == "todo"


@pytest.mark.asyncio
async def test_update_issue_status_not_found(db_session: AsyncSession):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await update_issue_status(db_session, 99999, status="done")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_issue_status_preserves_other_fields(db_session: AsyncSession):
    issue = Issue(title="Original", description="Desc", status="todo", priority="high")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    updated = await update_issue_status(db_session, issue.id, status="done")
    assert updated.title == "Original"
    assert updated.description == "Desc"
    assert updated.priority == "high"
    assert updated.status == "done"


@pytest.mark.asyncio
async def test_patch_status_endpoint(db_session: AsyncSession):
    from app.main import app

    issue = Issue(title="Test", status="todo")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch(
            f"/issues/{issue.id}/status",
            json={"status": "in_progress"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_progress"
    assert data["id"] == issue.id


@pytest.mark.asyncio
async def test_patch_status_endpoint_not_found(db_session: AsyncSession):
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch(
            "/issues/99999/status",
            json={"status": "done"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_status_endpoint_invalid_status(db_session: AsyncSession):
    from app.main import app

    issue = Issue(title="Test", status="todo")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch(
            f"/issues/{issue.id}/status",
            json={"status": "invalid"},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_patch_status_endpoint_returns_issue_response_shape(db_session: AsyncSession):
    from app.main import app

    issue = Issue(title="Shape test", status="todo", priority="low")
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.patch(
            f"/issues/{issue.id}/status",
            json={"status": "done"},
        )
    data = resp.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "status" in data
    assert "priority" in data
    assert "created_at" in data
    assert "updated_at" in data
