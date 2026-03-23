import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.webhook import Webhook, WebhookEvent
from src.personal_jira.schemas.webhook import WebhookCreate


class WebhookService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: WebhookCreate) -> Webhook:
        webhook = Webhook(
            name=data.name,
            url=data.url,
            webhook_type=data.webhook_type,
            events=[e.value for e in data.events],
            is_active=data.is_active,
        )
        self._session.add(webhook)
        await self._session.commit()
        await self._session.refresh(webhook)
        return webhook

    async def get(self, webhook_id: uuid.UUID) -> Webhook | None:
        result = await self._session.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Webhook]:
        result = await self._session.execute(
            select(Webhook).order_by(Webhook.created_at.desc())
        )
        return result.scalars().all()

    async def delete(self, webhook_id: uuid.UUID) -> bool:
        webhook = await self.get(webhook_id)
        if webhook is None:
            return False
        await self._session.delete(webhook)
        await self._session.commit()
        return True

    async def update(
        self, webhook_id: uuid.UUID, data: dict
    ) -> Webhook | None:
        webhook = await self.get(webhook_id)
        if webhook is None:
            return None
        for key, value in data.items():
            setattr(webhook, key, value)
        await self._session.commit()
        await self._session.refresh(webhook)
        return webhook

    async def get_active_for_event(
        self, event: WebhookEvent
    ) -> Sequence[Webhook]:
        result = await self._session.execute(
            select(Webhook).where(
                Webhook.is_active == True,
                Webhook.events.any(event.value),
            )
        )
        return result.scalars().all()
