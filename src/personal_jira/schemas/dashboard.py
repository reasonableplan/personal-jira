from __future__ import annotations

import uuid

from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class PriorityCount(BaseModel):
    priority: str
    count: int


class AssigneeCount(BaseModel):
    assignee_id: uuid.UUID | None
    count: int


class DashboardStats(BaseModel):
    total: int
    by_status: list[StatusCount]
    by_priority: list[PriorityCount]
    by_assignee: list[AssigneeCount]
    done_count: int
    completion_rate: float
