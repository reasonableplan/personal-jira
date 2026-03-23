from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from personal_jira.constants import BULK_UPDATE_MAX_ITEMS


class BulkUpdateItem(BaseModel):
    id: uuid.UUID
    status: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[list[str]] = None
    priority: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> BulkUpdateItem:
        update_fields = {"status", "assignee", "labels", "priority"}
        if not any(getattr(self, f) is not None for f in update_fields):
            raise ValueError("At least one update field must be provided")
        return self


class BulkUpdateRequest(BaseModel):
    items: list[BulkUpdateItem]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[BulkUpdateItem]) -> list[BulkUpdateItem]:
        if len(v) == 0:
            raise ValueError("items must not be empty")
        if len(v) > BULK_UPDATE_MAX_ITEMS:
            raise ValueError(f"items must not exceed {BULK_UPDATE_MAX_ITEMS}")
        return v


class BulkUpdateResultItem(BaseModel):
    id: uuid.UUID
    success: bool
    error: Optional[str] = None


class BulkUpdateResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[BulkUpdateResultItem]
