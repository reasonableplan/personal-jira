import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.dependencies import get_session
from personal_jira.schemas.webhook import WebhookCreate, WebhookResponse, WebhookUpdate
from personal_jira.services.webhook import WebhookService

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


def _to_response(wh: "Webhook") -> dict:  # type: ignore[name-defined]
    return {
        "id": str(wh.id),
        "url": wh.url,
        "event_types": json.loads(wh.event_types),
        "is_active": wh.is_active,
        "created_at": str(wh.created_at),
        "updated_at": str(wh.updated_at),
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_webhook(
    payload: WebhookCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    svc = WebhookService(session)
    wh = await svc.create(
        url=str(payload.url),
        event_types=payload.event_types,
        secret=payload.secret,
    )
    return _to_response(wh)


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(session: AsyncSession = Depends(get_session)) -> list[dict]:
    svc = WebhookService(session)
    webhooks = await svc.list_all()
    return [_to_response(wh) for wh in webhooks]


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> None:
    svc = WebhookService(session)
    deleted = await svc.delete(webhook_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Webhook not found")


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: uuid.UUID,
    payload: WebhookUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    svc = WebhookService(session)
    wh = await svc.update(webhook_id, is_active=payload.is_active)
    if not wh:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return _to_response(wh)
