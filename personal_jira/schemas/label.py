from pydantic import BaseModel, field_validator

MIN_LABEL_LENGTH = 1
MAX_LABEL_LENGTH = 50


class LabelAddRequest(BaseModel):
    labels: list[str]

    @field_validator("labels", mode="before")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        stripped = [label.strip() for label in v]
        for label in stripped:
            if len(label) < MIN_LABEL_LENGTH or len(label) > MAX_LABEL_LENGTH:
                raise ValueError(f"Label must be between {MIN_LABEL_LENGTH} and {MAX_LABEL_LENGTH} characters")
        deduplicated = list(dict.fromkeys(stripped))
        if not deduplicated:
            raise ValueError("At least one label is required")
        return deduplicated


class LabelRemoveRequest(BaseModel):
    labels: list[str]

    @field_validator("labels", mode="before")
    @classmethod
    def validate_labels(cls, v: list[str]) -> list[str]:
        stripped = [label.strip() for label in v]
        if not stripped:
            raise ValueError("At least one label is required")
        return list(dict.fromkeys(stripped))


class LabelListResponse(BaseModel):
    labels: list[str]
    count: int
