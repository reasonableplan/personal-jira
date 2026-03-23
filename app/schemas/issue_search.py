from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.issue import IssueStatus, IssuePriority, IssueType

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "priority", "title", "status"}
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
UNASSIGNED_SENTINEL = "__unassigned__"


class IssueSearchParams(BaseModel):
    status: Optional[list[IssueStatus]] = None
    priority: Optional[list[IssuePriority]] = None
    assignee: Optional[str] = None
    label: Optional[list[str]] = None
    issue_type: Optional[IssueType] = None
    q: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    offset: int = 0
    limit: int = DEFAULT_LIMIT

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        if v not in ALLOWED_SORT_FIELDS:
            raise ValueError(f"sort_by must be one of {ALLOWED_SORT_FIELDS}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        if v not in {"asc", "desc"}:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

    @field_validator("limit")
    @classmethod
    def clamp_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError("limit must be >= 1")
        return min(v, MAX_LIMIT)

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("offset must be >= 0")
        return v
