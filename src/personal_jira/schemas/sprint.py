from datetime import date, datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from personal_jira.models.sprint import SprintStatus


class SprintCreate(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: date
    end_date: date

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @model_validator(mode="after")
    def end_after_start(self) -> "SprintCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[SprintStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SprintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    goal: Optional[str]
    status: SprintStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


class SprintListResponse(BaseModel):
    items: list[SprintResponse]
    total: int
    offset: int
    limit: int


class SprintIssueAdd(BaseModel):
    issue_id: UUID
