import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.personal_jira.models.webhook import WebhookType, WebhookEvent


class WebhookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=2048)
    webhook_type: WebhookType
    events: list[WebhookEvent] = Field(..., min_length=1)
    is_active: bool = True

    @field_validator("events")
    @classmethod
    def events_not_empty(cls, v: list[WebhookEvent]) -> list[WebhookEvent]:
        if not v:
            raise ValueError("events must not be empty")
        return v


class WebhookUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1, max_length=2048)
    events: list[WebhookEvent] | None = None
    is_active: bool | None = None


class WebhookResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    webhook_type: WebhookType
    events: list[WebhookEvent]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookListResponse(BaseModel):
    items: list[WebhookResponse]


class WebhookTestResponse(BaseModel):
    success: bool
    message: str
