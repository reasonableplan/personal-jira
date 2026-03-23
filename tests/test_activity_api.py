import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from personal_jira.app import create_app
from personal_jira.database import get_async_session
from personal_jira.models.activity import ActivityType
from personal_jira.models.issue import Issue
from personal_jira.services.activity_service import ActivityService


@pytest.fixture
def app(db_session):
    application = create_app()

    async def override_session():
        yield db_session

    application.dependency_overrides[get_async_session] = override_session
    return application


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
async def sample_issue(db_session) -> Issue:
    issue = Issue(
        id=uuid.uuid4(),
        title="Test Issue",
        status="Backlog",
        priority="Medium",
    )
    db_session.add(issue)
    await db_session.commit()
    await db_session.refresh(issue)
    return issue


class TestGetActivities:
    @pytest.mark.asyncio
    async def test_empty_timeline(
        self, client: AsyncClient, sample_issue: Issue
    ) -> None:
        resp = await client.get(f"/api/v1/issues/{sample_issue.id}/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_returns_activities(
        self, client: AsyncClient, sample_issue: Issue, db_session
    ) -> None:
        service = ActivityService(db_session)
        await service.record(
            issue_id=sample_issue.id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
            new_value=sample_issue.title,
        )
        await service.record(
            issue_id=sample_issue.id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )

        resp = await client.get(f"/api/v1/issues/{sample_issue.id}/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_pagination(
        self, client: AsyncClient, sample_issue: Issue, db_session
    ) -> None:
        service = ActivityService(db_session)
        for i in range(5):
            await service.record(
                issue_id=sample_issue.id,
                activity_type=ActivityType.STATUS_CHANGED,
                actor="user-1",
                old_value=f"s{i}",
                new_value=f"s{i + 1}",
            )

        resp = await client.get(
            f"/api/v1/issues/{sample_issue.id}/activities?offset=0&limit=2"
        )
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    @pytest.mark.asyncio
    async def test_filter_by_type(
        self, client: AsyncClient, sample_issue: Issue, db_session
    ) -> None:
        service = ActivityService(db_session)
        await service.record(
            issue_id=sample_issue.id,
            activity_type=ActivityType.CREATED,
            actor="user-1",
        )
        await service.record(
            issue_id=sample_issue.id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )

        resp = await client.get(
            f"/api/v1/issues/{sample_issue.id}/activities?activity_type=status_changed"
        )
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["activity_type"] == "status_changed"

    @pytest.mark.asyncio
    async def test_nonexistent_issue(
        self, client: AsyncClient
    ) -> None:
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/issues/{fake_id}/activities")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_uuid(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/issues/not-a-uuid/activities")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_activity_response_shape(
        self, client: AsyncClient, sample_issue: Issue, db_session
    ) -> None:
        service = ActivityService(db_session)
        await service.record(
            issue_id=sample_issue.id,
            activity_type=ActivityType.STATUS_CHANGED,
            actor="user-1",
            old_value="Backlog",
            new_value="Ready",
        )

        resp = await client.get(f"/api/v1/issues/{sample_issue.id}/activities")
        item = resp.json()["items"][0]
        assert "id" in item
        assert "issue_id" in item
        assert "activity_type" in item
        assert "actor" in item
        assert "old_value" in item
        assert "new_value" in item
        assert "detail" in item
        assert "created_at" in item
