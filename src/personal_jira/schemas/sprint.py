from datetime import date
from uuid import UUID

from pydantic import BaseModel, model_validator

from personal_jira.models.sprint import SprintStatus


class SprintCreate(BaseModel):
    name: str
    goal: str | None = None
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "SprintCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        if not self.name.strip():
            raise ValueError("name must not be empty")
        return self


class SprintUpdate(BaseModel):
    name: str | None = None
    goal: str | None = None
    status: SprintStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class SprintResponse(BaseModel):
    id: UUID
    name: str
    goal: str | None = None
    status: str
    start_date: date
    end_date: date

    model_config = {"from_attributes": True}


class SprintListResponse(BaseModel):
    items: list[SprintResponse]
    total: int


class SprintIssueAdd(BaseModel):
    issue_id: UUID
