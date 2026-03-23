from __future__ import annotations

import enum
from typing import Annotated

from pydantic import BaseModel, Field


class LabelPatchAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    SET = "set"


class LabelUpdate(BaseModel):
    """Replace the entire label list."""

    labels: list[str] = Field(default_factory=list)


class LabelPatch(BaseModel):
    """Partial label update — add, remove, or set labels."""

    action: LabelPatchAction
    labels: list[str] = Field(default_factory=list)


class LabelListResponse(BaseModel):
    """Response containing a list of labels for an issue."""

    issue_id: str
    labels: list[str] = Field(default_factory=list)
