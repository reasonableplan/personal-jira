from uuid import UUID

from pydantic import BaseModel, model_validator


class TemplateCreate(BaseModel):
    name: str
    title_pattern: str
    description_template: str | None = None
    default_priority: str | None = None
    default_issue_type: str | None = None
    default_labels: list[str] | None = None

    @model_validator(mode="after")
    def validate_fields(self) -> "TemplateCreate":
        if not self.name.strip():
            raise ValueError("name must not be empty")
        if not self.title_pattern.strip():
            raise ValueError("title_pattern must not be empty")
        return self


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    title_pattern: str
    description_template: str | None = None
    default_priority: str | None = None
    default_issue_type: str | None = None
    default_labels: list[str] | None = None

    model_config = {"from_attributes": True}


class CreateFromTemplateRequest(BaseModel):
    variables: dict[str, str] = {}


class CloneIssueRequest(BaseModel):
    title_prefix: str | None = None
    reset_status: bool = True


class TemplateIssueCreate(BaseModel):
    summary: str
