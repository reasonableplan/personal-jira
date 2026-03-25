import re

from pydantic import BaseModel, field_validator

COLOR_HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _validate_hex_color(v: str) -> str:
    if not COLOR_HEX_PATTERN.match(v):
        raise ValueError("color must be #RRGGBB hex format")
    return v.upper()


class LabelCreate(BaseModel):
    name: str
    color: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        return _validate_hex_color(v)


class LabelUpdate(BaseModel):
    name: str | None = None
    color: str | None = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_hex_color(v)


class LabelResponse(BaseModel):
    id: str
    name: str
    color: str

    model_config = {"from_attributes": True}


class TaskLabelsAttach(BaseModel):
    label_ids: list[str]
