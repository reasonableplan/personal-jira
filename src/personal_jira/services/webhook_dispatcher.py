import logging
from datetime import datetime, timezone

import httpx

from src.personal_jira.models.webhook import Webhook, WebhookType, WebhookEvent

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_SECONDS = 10

EVENT_LABELS: dict[WebhookEvent, str] = {
    WebhookEvent.ISSUE_CREATED: "Issue Created",
    WebhookEvent.ISSUE_UPDATED: "Issue Updated",
    WebhookEvent.ISSUE_DELETED: "Issue Deleted",
    WebhookEvent.ISSUE_TRANSITIONED: "Issue Transitioned",
    WebhookEvent.ISSUE_COMMENT_ADDED: "Comment Added",
}

EVENT_COLORS: dict[WebhookEvent, int] = {
    WebhookEvent.ISSUE_CREATED: 0x2ECC71,
    WebhookEvent.ISSUE_UPDATED: 0x3498DB,
    WebhookEvent.ISSUE_DELETED: 0xE74C3C,
    WebhookEvent.ISSUE_TRANSITIONED: 0xF39C12,
    WebhookEvent.ISSUE_COMMENT_ADDED: 0x9B59B6,
}


class WebhookDispatcher:
    def build_payload(
        self,
        webhook_type: WebhookType,
        event: WebhookEvent,
        data: dict,
    ) -> dict:
        label = EVENT_LABELS.get(event, event.value)
        if webhook_type == WebhookType.DISCORD:
            return self._build_discord_payload(event, label, data)
        return self._build_slack_payload(event, label, data)

    def _build_discord_payload(
        self, event: WebhookEvent, label: str, data: dict
    ) -> dict:
        color = EVENT_COLORS.get(event, 0x95A5A6)
        fields = [
            {"name": k, "value": str(v), "inline": True}
            for k, v in data.items()
            if k != "title"
        ]
        return {
            "embeds": [
                {
                    "title": f"[{label}] {data.get('title', 'N/A')}",
                    "color": color,
                    "fields": fields,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ]
        }

    def _build_slack_payload(
        self, event: WebhookEvent, label: str, data: dict
    ) -> dict:
        text_lines = [f"*{label}*: {data.get('title', 'N/A')}"]
        for k, v in data.items():
            if k != "title":
                text_lines.append(f"• *{k}*: {v}")
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "\n".join(text_lines),
                    },
                }
            ]
        }

    async def send(
        self,
        webhook: Webhook,
        event: WebhookEvent,
        data: dict,
    ) -> bool:
        payload = self.build_payload(webhook.webhook_type, event, data)
        try:
            async with httpx.AsyncClient(
                timeout=WEBHOOK_TIMEOUT_SECONDS
            ) as client:
                response = await client.post(webhook.url, json=payload)
                response.raise_for_status()
            return True
        except Exception:
            logger.exception(
                "Failed to send webhook '%s' to %s", webhook.name, webhook.url
            )
            return False

    async def dispatch_event(
        self,
        webhooks: list[Webhook],
        event: WebhookEvent,
        data: dict,
    ) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for wh in webhooks:
            results[str(wh.id)] = await self.send(wh, event, data)
        return results
