import uuid
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

from personal_jira.models.webhook import Webhook, WebhookEventType
from personal_jira.schemas.webhook import WebhookCreate, WebhookResponse
from personal_jira.services.webhook import WebhookService


API_PREFIX = "/api/v1/webhooks"


@pytest.mark.asyncio
class TestWebhookModel:
    async def test_webhook_table_name(self) -> None:
        assert Webhook.__tablename__ == "webhooks"

    async def test_webhook_has_required_columns(self) -> None:
        columns = {c.name for c in Webhook.__table__.columns}
        assert "id" in columns
        assert "url" in columns
        assert "event_types" in columns
        assert "secret" in columns
        assert "is_active" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    async def test_event_type_enum_values(self) -> None:
        assert WebhookEventType.ISSUE_CREATED.value == "issue.created"
        assert WebhookEventType.ISSUE_UPDATED.value == "issue.updated"
        assert WebhookEventType.ISSUE_DELETED.value == "issue.deleted"
        assert WebhookEventType.ISSUE_TRANSITIONED.value == "issue.transitioned"
        assert WebhookEventType.COMMENT_ADDED.value == "comment.added"


@pytest.mark.asyncio
class TestWebhookSchema:
    async def test_create_schema_required_fields(self) -> None:
        data = WebhookCreate(url="https://example.com/hook", event_types=["issue.created"])
        assert str(data.url) == "https://example.com/hook"
        assert data.event_types == ["issue.created"]

    async def test_create_schema_optional_secret(self) -> None:
        data = WebhookCreate(url="https://example.com/hook", event_types=["issue.created"])
        assert data.secret is None

    async def test_response_schema(self) -> None:
        resp = WebhookResponse(
            id=uuid.uuid4(),
            url="https://example.com/hook",
            event_types=["issue.created"],
            is_active=True,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        assert resp.is_active is True


@pytest.mark.asyncio
class TestWebhookAPI:
    async def test_register_webhook(self, client: AsyncClient) -> None:
        resp = await client.post(API_PREFIX, json={
            "url": "https://example.com/hook",
            "event_types": ["issue.created"],
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["url"] == "https://example.com/hook"
        assert body["event_types"] == ["issue.created"]
        assert body["is_active"] is True

    async def test_register_webhook_with_secret(self, client: AsyncClient) -> None:
        resp = await client.post(API_PREFIX, json={
            "url": "https://example.com/hook",
            "event_types": ["issue.created"],
            "secret": "my-secret-token",
        })
        assert resp.status_code == 201
        assert "secret" not in resp.json()

    async def test_register_webhook_invalid_url(self, client: AsyncClient) -> None:
        resp = await client.post(API_PREFIX, json={
            "url": "not-a-url",
            "event_types": ["issue.created"],
        })
        assert resp.status_code == 422

    async def test_register_webhook_empty_events(self, client: AsyncClient) -> None:
        resp = await client.post(API_PREFIX, json={
            "url": "https://example.com/hook",
            "event_types": [],
        })
        assert resp.status_code == 422

    async def test_list_webhooks(self, client: AsyncClient) -> None:
        await client.post(API_PREFIX, json={
            "url": "https://a.com/hook",
            "event_types": ["issue.created"],
        })
        await client.post(API_PREFIX, json={
            "url": "https://b.com/hook",
            "event_types": ["issue.updated"],
        })
        resp = await client.get(API_PREFIX)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_delete_webhook(self, client: AsyncClient) -> None:
        create_resp = await client.post(API_PREFIX, json={
            "url": "https://example.com/hook",
            "event_types": ["issue.created"],
        })
        wh_id = create_resp.json()["id"]
        del_resp = await client.delete(f"{API_PREFIX}/{wh_id}")
        assert del_resp.status_code == 204
        get_resp = await client.get(API_PREFIX)
        assert len(get_resp.json()) == 0

    async def test_delete_webhook_not_found(self, client: AsyncClient) -> None:
        resp = await client.delete(f"{API_PREFIX}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_toggle_webhook(self, client: AsyncClient) -> None:
        create_resp = await client.post(API_PREFIX, json={
            "url": "https://example.com/hook",
            "event_types": ["issue.created"],
        })
        wh_id = create_resp.json()["id"]
        resp = await client.patch(f"{API_PREFIX}/{wh_id}", json={"is_active": False})
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False


@pytest.mark.asyncio
class TestWebhookDelivery:
    @patch("personal_jira.services.webhook.httpx.AsyncClient")
    async def test_dispatch_sends_to_active_webhooks(
        self, mock_client_cls: AsyncMock, session: Any, sample_issue: dict[str, Any]
    ) -> None:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        svc = WebhookService(session)
        webhook = Webhook(
            id=uuid.uuid4(),
            url="https://example.com/hook",
            event_types=["issue.created"],
            is_active=True,
        )
        session.add(webhook)
        await session.commit()

        await svc.dispatch("issue.created", {"issue_id": sample_issue["id"]})
        mock_client.post.assert_called_once()

    @patch("personal_jira.services.webhook.httpx.AsyncClient")
    async def test_dispatch_skips_inactive_webhooks(
        self, mock_client_cls: AsyncMock, session: Any
    ) -> None:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        svc = WebhookService(session)
        webhook = Webhook(
            id=uuid.uuid4(),
            url="https://example.com/hook",
            event_types=["issue.created"],
            is_active=False,
        )
        session.add(webhook)
        await session.commit()

        await svc.dispatch("issue.created", {"issue_id": "abc"})
        mock_client.post.assert_not_called()

    @patch("personal_jira.services.webhook.httpx.AsyncClient")
    async def test_dispatch_skips_non_matching_events(
        self, mock_client_cls: AsyncMock, session: Any
    ) -> None:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        svc = WebhookService(session)
        webhook = Webhook(
            id=uuid.uuid4(),
            url="https://example.com/hook",
            event_types=["issue.deleted"],
            is_active=True,
        )
        session.add(webhook)
        await session.commit()

        await svc.dispatch("issue.created", {"issue_id": "abc"})
        mock_client.post.assert_not_called()

    @patch("personal_jira.services.webhook.httpx.AsyncClient")
    async def test_dispatch_includes_hmac_signature(
        self, mock_client_cls: AsyncMock, session: Any
    ) -> None:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        svc = WebhookService(session)
        webhook = Webhook(
            id=uuid.uuid4(),
            url="https://example.com/hook",
            event_types=["issue.created"],
            is_active=True,
            secret="test-secret",
        )
        session.add(webhook)
        await session.commit()

        await svc.dispatch("issue.created", {"issue_id": "abc"})
        call_kwargs = mock_client.post.call_args
        headers = call_kwargs.kwargs.get("headers", {})
        assert "X-Webhook-Signature" in headers
