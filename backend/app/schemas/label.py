import re
from typing import Optional

from pydantic import BaseModel, field_validator

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class LabelCreate(BaseModel):
    name: str
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not HEX_COLOR_PATTERN.match(v):
            raise ValueError("color must be #RRGGBB hex format")
        return v


class LabelUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not HEX_COLOR_PATTERN.match(v):
            raise ValueError("color must be #RRGGBB hex format")
        return v


class LabelResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    color: str


class TaskLabelsAttach(BaseModel):
    label_ids: list[str]
