import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.personal_jira.database import Base, get_db
from src.personal_jira.models.webhook import Webhook, WebhookType, WebhookEvent
from src.personal_jira.schemas.webhook import (
    WebhookCreate,
    WebhookResponse,
    WebhookListResponse,
)
from src.personal_jira.services.webhook_service import WebhookService
from src.personal_jira.services.webhook_dispatcher import WebhookDispatcher
from src.personal_jira.app import create_app


TEST_DATABASE_URL = "sqlite+aiosqlite:///"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    app = create_app()
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestWebhookModel:
    def test_webhook_type_values(self):
        assert WebhookType.DISCORD == "discord"
        assert WebhookType.SLACK == "slack"

    def test_webhook_event_values(self):
        assert WebhookEvent.ISSUE_CREATED == "issue_created"
        assert WebhookEvent.ISSUE_UPDATED == "issue_updated"
        assert WebhookEvent.ISSUE_DELETED == "issue_deleted"
        assert WebhookEvent.ISSUE_TRANSITIONED == "issue_transitioned"
        assert WebhookEvent.ISSUE_COMMENT_ADDED == "issue_comment_added"

    @pytest.mark.asyncio
    async def test_create_webhook(self, session: AsyncSession):
        webhook = Webhook(
            name="test-hook",
            url="https://discord.com/api/webhooks/123/abc",
            webhook_type=WebhookType.DISCORD,
            events=[WebhookEvent.ISSUE_CREATED, WebhookEvent.ISSUE_UPDATED],
            is_active=True,
        )
        session.add(webhook)
        await session.commit()
        await session.refresh(webhook)

        assert webhook.id is not None
        assert webhook.name == "test-hook"
        assert webhook.webhook_type == WebhookType.DISCORD
        assert WebhookEvent.ISSUE_CREATED in webhook.events
        assert webhook.is_active is True
        assert webhook.created_at is not None
        assert webhook.updated_at is not None

    @pytest.mark.asyncio
    async def test_webhook_default_active(self, session: AsyncSession):
        webhook = Webhook(
            name="default-hook",
            url="https://hooks.slack.com/services/T/B/xxx",
            webhook_type=WebhookType.SLACK,
            events=[WebhookEvent.ISSUE_CREATED],
        )
        session.add(webhook)
        await session.commit()
        await session.refresh(webhook)
        assert webhook.is_active is True


class TestWebhookSchema:
    def test_webhook_create_valid(self):
        data = WebhookCreate(
            name="my-hook",
            url="https://discord.com/api/webhooks/123/abc",
            webhook_type=WebhookType.DISCORD,
            events=[WebhookEvent.ISSUE_CREATED],
        )
        assert data.name == "my-hook"
        assert data.is_active is True

    def test_webhook_create_defaults(self):
        data = WebhookCreate(
            name="hook",
            url="https://hooks.slack.com/services/T/B/x",
            webhook_type=WebhookType.SLACK,
            events=[WebhookEvent.ISSUE_CREATED, WebhookEvent.ISSUE_UPDATED],
        )
        assert data.is_active is True

    def test_webhook_create_empty_events_rejected(self):
        with pytest.raises(Exception):
            WebhookCreate(
                name="hook",
                url="https://discord.com/api/webhooks/123/abc",
                webhook_type=WebhookType.DISCORD,
                events=[],
            )

    def test_webhook_create_empty_name_rejected(self):
        with pytest.raises(Exception):
            WebhookCreate(
                name="",
                url="https://discord.com/api/webhooks/123/abc",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED],
            )


class TestWebhookService:
    @pytest.mark.asyncio
    async def test_create_webhook(self, session: AsyncSession):
        service = WebhookService(session)
        webhook = await service.create(
            WebhookCreate(
                name="svc-hook",
                url="https://discord.com/api/webhooks/111/def",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED],
            )
        )
        assert webhook.id is not None
        assert webhook.name == "svc-hook"

    @pytest.mark.asyncio
    async def test_get_webhook(self, session: AsyncSession):
        service = WebhookService(session)
        created = await service.create(
            WebhookCreate(
                name="get-hook",
                url="https://hooks.slack.com/services/T/B/y",
                webhook_type=WebhookType.SLACK,
                events=[WebhookEvent.ISSUE_UPDATED],
            )
        )
        found = await service.get(created.id)
        assert found is not None
        assert found.id == created.id

    @pytest.mark.asyncio
    async def test_get_webhook_not_found(self, session: AsyncSession):
        service = WebhookService(session)
        found = await service.get(uuid.uuid4())
        assert found is None

    @pytest.mark.asyncio
    async def test_list_webhooks(self, session: AsyncSession):
        service = WebhookService(session)
        for i in range(3):
            await service.create(
                WebhookCreate(
                    name=f"hook-{i}",
                    url=f"https://discord.com/api/webhooks/{i}/abc",
                    webhook_type=WebhookType.DISCORD,
                    events=[WebhookEvent.ISSUE_CREATED],
                )
            )
        webhooks = await service.list_all()
        assert len(webhooks) == 3

    @pytest.mark.asyncio
    async def test_delete_webhook(self, session: AsyncSession):
        service = WebhookService(session)
        created = await service.create(
            WebhookCreate(
                name="del-hook",
                url="https://discord.com/api/webhooks/999/xyz",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED],
            )
        )
        deleted = await service.delete(created.id)
        assert deleted is True
        assert await service.get(created.id) is None

    @pytest.mark.asyncio
    async def test_delete_webhook_not_found(self, session: AsyncSession):
        service = WebhookService(session)
        deleted = await service.delete(uuid.uuid4())
        assert deleted is False

    @pytest.mark.asyncio
    async def test_update_webhook(self, session: AsyncSession):
        service = WebhookService(session)
        created = await service.create(
            WebhookCreate(
                name="upd-hook",
                url="https://discord.com/api/webhooks/777/uvw",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED],
            )
        )
        updated = await service.update(
            created.id, {"name": "updated-hook", "is_active": False}
        )
        assert updated is not None
        assert updated.name == "updated-hook"
        assert updated.is_active is False

    @pytest.mark.asyncio
    async def test_get_active_for_event(self, session: AsyncSession):
        service = WebhookService(session)
        await service.create(
            WebhookCreate(
                name="active-hook",
                url="https://discord.com/api/webhooks/1/a",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED, WebhookEvent.ISSUE_UPDATED],
            )
        )
        inactive = await service.create(
            WebhookCreate(
                name="inactive-hook",
                url="https://discord.com/api/webhooks/2/b",
                webhook_type=WebhookType.DISCORD,
                events=[WebhookEvent.ISSUE_CREATED],
                is_active=False,
            )
        )
        await service.update(inactive.id, {"is_active": False})
        active = await service.get_active_for_event(WebhookEvent.ISSUE_CREATED)
        assert len(active) == 1
        assert active[0].name == "active-hook"


class TestWebhookDispatcher:
    @pytest.mark.asyncio
    async def test_build_discord_payload(self):
        dispatcher = WebhookDispatcher()
        payload = dispatcher.build_payload(
            webhook_type=WebhookType.DISCORD,
            event=WebhookEvent.ISSUE_CREATED,
            data={"title": "Bug #1", "id": "abc-123"},
        )
        assert "embeds" in payload
        assert payload["embeds"][0]["title"] is not None

    @pytest.mark.asyncio
    async def test_build_slack_payload(self):
        dispatcher = WebhookDispatcher()
        payload = dispatcher.build_payload(
            webhook_type=WebhookType.SLACK,
            event=WebhookEvent.ISSUE_CREATED,
            data={"title": "Bug #1", "id": "abc-123"},
        )
        assert "blocks" in payload

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_dispatch_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        dispatcher = WebhookDispatcher()
        webhook = Webhook(
            id=uuid.uuid4(),
            name="test",
            url="https://discord.com/api/webhooks/1/a",
            webhook_type=WebhookType.DISCORD,
            events=[WebhookEvent.ISSUE_CREATED],
            is_active=True,
        )
        result = await dispatcher.send(
            webhook=webhook,
            event=WebhookEvent.ISSUE_CREATED,
            data={"title": "Test", "id": "x"},
        )
        assert result is True

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.post")
    async def test_dispatch_failure_logs_error(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")

        dispatcher = WebhookDispatcher()
        webhook = Webhook(
            id=uuid.uuid4(),
            name="fail-hook",
            url="https://discord.com/api/webhooks/bad/url",
            webhook_type=WebhookType.DISCORD,
            events=[WebhookEvent.ISSUE_CREATED],
            is_active=True,
        )
        result = await dispatcher.send(
            webhook=webhook,
            event=WebhookEvent.ISSUE_CREATED,
            data={"title": "Test", "id": "x"},
        )
        assert result is False


class TestWebhookAPI:
    @pytest.mark.asyncio
    async def test_create_webhook_endpoint(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "api-hook",
                "url": "https://discord.com/api/webhooks/123/abc",
                "webhook_type": "discord",
                "events": ["issue_created"],
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "api-hook"
        assert body["webhook_type"] == "discord"
        assert body["is_active"] is True
        assert "id" in body

    @pytest.mark.asyncio
    async def test_create_webhook_missing_name(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/webhooks",
            json={
                "url": "https://discord.com/api/webhooks/123/abc",
                "webhook_type": "discord",
                "events": ["issue_created"],
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_webhook_empty_events(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "hook",
                "url": "https://discord.com/api/webhooks/123/abc",
                "webhook_type": "discord",
                "events": [],
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_list_webhooks_endpoint(self, client: AsyncClient):
        for i in range(2):
            await client.post(
                "/api/v1/webhooks",
                json={
                    "name": f"hook-{i}",
                    "url": f"https://discord.com/api/webhooks/{i}/abc",
                    "webhook_type": "discord",
                    "events": ["issue_created"],
                },
            )
        resp = await client.get("/api/v1/webhooks")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_webhook_endpoint(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "get-hook",
                "url": "https://hooks.slack.com/services/T/B/x",
                "webhook_type": "slack",
                "events": ["issue_updated"],
            },
        )
        webhook_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/webhooks/{webhook_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "get-hook"

    @pytest.mark.asyncio
    async def test_get_webhook_not_found(self, client: AsyncClient):
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/webhooks/{fake_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_webhook_endpoint(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "del-hook",
                "url": "https://discord.com/api/webhooks/999/xyz",
                "webhook_type": "discord",
                "events": ["issue_created"],
            },
        )
        webhook_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/webhooks/{webhook_id}")
        assert resp.status_code == 204
        get_resp = await client.get(f"/api/v1/webhooks/{webhook_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_webhook_not_found(self, client: AsyncClient):
        fake_id = str(uuid.uuid4())
        resp = await client.delete(f"/api/v1/webhooks/{fake_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_webhook_endpoint(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "patch-hook",
                "url": "https://discord.com/api/webhooks/555/rst",
                "webhook_type": "discord",
                "events": ["issue_created"],
            },
        )
        webhook_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/api/v1/webhooks/{webhook_id}",
            json={"name": "patched", "is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "patched"
        assert resp.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_patch_webhook_not_found(self, client: AsyncClient):
        fake_id = str(uuid.uuid4())
        resp = await client.patch(
            f"/api/v1/webhooks/{fake_id}", json={"name": "x"}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_test_webhook_endpoint(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/webhooks",
            json={
                "name": "test-hook",
                "url": "https://discord.com/api/webhooks/888/test",
                "webhook_type": "discord",
                "events": ["issue_created"],
            },
        )
        webhook_id = create_resp.json()["id"]
        with patch(
            "src.personal_jira.services.webhook_dispatcher.WebhookDispatcher.send",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = await client.post(f"/api/v1/webhooks/{webhook_id}/test")
            assert resp.status_code == 200
            assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_uuid_returns_422(self, client: AsyncClient):
        resp = await client.get("/api/v1/webhooks/not-a-uuid")
        assert resp.status_code == 422
