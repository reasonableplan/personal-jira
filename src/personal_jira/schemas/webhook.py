import uuid
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_types: list[str] = Field(..., min_length=1)
    secret: Optional[str] = None


class WebhookUpdate(BaseModel):
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: uuid.UUID
    url: str
    event_types: list[str]
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
