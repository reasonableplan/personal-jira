import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from personal_jira.models.context_bundle import BundleItemType


class BundleItemCreate(BaseModel):
    item_type: BundleItemType
    path: Optional[str] = None
    content: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class BundleItemResponse(BaseModel):
    id: uuid.UUID
    item_type: BundleItemType
    path: Optional[str]
    content: Optional[str]
    line_start: Optional[int]
    line_end: Optional[int]

    model_config = {"from_attributes": True}


class ContextBundleCreate(BaseModel):
    items: list[BundleItemCreate]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[BundleItemCreate]) -> list[BundleItemCreate]:
        if not v:
            raise ValueError("items must not be empty")
        return v


class ContextBundleResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    items: list[BundleItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
