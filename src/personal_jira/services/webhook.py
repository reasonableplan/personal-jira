import hashlib
import hmac
import json
import logging
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.config import WEBHOOK_TIMEOUT_SECONDS
from personal_jira.models.webhook import Webhook

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, url: str, event_types: list[str], secret: str | None = None) -> Webhook:
        webhook = Webhook(
            url=url,
            event_types=json.dumps(event_types),
            secret=secret,
            is_active=True,
        )
        self._session.add(webhook)
        await self._session.commit()
        await self._session.refresh(webhook)
        return webhook

    async def list_all(self) -> list[Webhook]:
        result = await self._session.execute(select(Webhook))
        return list(result.scalars().all())

    async def delete(self, webhook_id: Any) -> bool:
        webhook = await self._session.get(Webhook, webhook_id)
        if not webhook:
            return False
        await self._session.delete(webhook)
        await self._session.commit()
        return True

    async def update(self, webhook_id: Any, is_active: bool | None = None) -> Webhook | None:
        webhook = await self._session.get(Webhook, webhook_id)
        if not webhook:
            return None
        if is_active is not None:
            webhook.is_active = is_active
        await self._session.commit()
        await self._session.refresh(webhook)
        return webhook

    async def dispatch(self, event_type: str, payload: dict[str, Any]) -> None:
        result = await self._session.execute(select(Webhook).where(Webhook.is_active == True))  # noqa: E712
        webhooks = result.scalars().all()

        body = json.dumps({"event": event_type, "data": payload})

        async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT_SECONDS) as client:
            for wh in webhooks:
                stored_events: list[str] = json.loads(wh.event_types)
                if event_type not in stored_events:
                    continue
                headers: dict[str, str] = {"Content-Type": "application/json"}
                if wh.secret:
                    sig = hmac.new(wh.secret.encode(), body.encode(), hashlib.sha256).hexdigest()
                    headers["X-Webhook-Signature"] = f"sha256={sig}"
                try:
                    await client.post(wh.url, content=body, headers=headers)
                except httpx.HTTPError as exc:
                    logger.error("Webhook delivery failed for %s: %s", wh.url, exc)

    def _to_response(self, webhook: Webhook) -> dict[str, Any]:
        return {
            "id": str(webhook.id),
            "url": webhook.url,
            "event_types": json.loads(webhook.event_types),
            "is_active": webhook.is_active,
            "created_at": str(webhook.created_at),
            "updated_at": str(webhook.updated_at),
        }
