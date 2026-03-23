import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.models.webhook import WebhookEvent
from src.personal_jira.services.webhook_service import WebhookService
from src.personal_jira.services.webhook_dispatcher import WebhookDispatcher

logger = logging.getLogger(__name__)


class WebhookEventHandler:
    def __init__(self, session: AsyncSession) -> None:
        self._service = WebhookService(session)
        self._dispatcher = WebhookDispatcher()

    async def handle(self, event: WebhookEvent, data: dict) -> None:
        webhooks = await self._service.get_active_for_event(event)
        if not webhooks:
            return
        results = await self._dispatcher.dispatch_event(
            list(webhooks), event, data
        )
        failed = [wid for wid, ok in results.items() if not ok]
        if failed:
            logger.warning(
                "Webhook delivery failed for %d/%d hooks on event %s",
                len(failed),
                len(results),
                event.value,
            )
