import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.personal_jira.database import get_db
from src.personal_jira.models.webhook import WebhookEvent
from src.personal_jira.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
    WebhookTestResponse,
)
from src.personal_jira.services.webhook_service import WebhookService
from src.personal_jira.services.webhook_dispatcher import WebhookDispatcher

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_dispatcher = WebhookDispatcher()


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    data: WebhookCreate,
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    service = WebhookService(db)
    webhook = await service.create(data)
    return WebhookResponse.model_validate(webhook)


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
) -> WebhookListResponse:
    service = WebhookService(db)
    webhooks = await service.list_all()
    return WebhookListResponse(
        items=[WebhookResponse.model_validate(w) for w in webhooks]
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    service = WebhookService(db)
    webhook = await service.get(webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return WebhookResponse.model_validate(webhook)


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: uuid.UUID,
    data: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    service = WebhookService(db)
    update_data = data.model_dump(exclude_unset=True)
    webhook = await service.update(webhook_id, update_data)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return WebhookResponse.model_validate(webhook)


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = WebhookService(db)
    deleted = await service.delete(webhook_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Webhook not found")


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> WebhookTestResponse:
    service = WebhookService(db)
    webhook = await service.get(webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found")
    test_data = {
        "title": "Test Notification",
        "id": str(webhook_id),
        "status": "test",
    }
    success = await _dispatcher.send(
        webhook=webhook,
        event=WebhookEvent.ISSUE_CREATED,
        data=test_data,
    )
    return WebhookTestResponse(
        success=success,
        message="Webhook delivered successfully" if success else "Webhook delivery failed",
    )
