from __future__ import annotations

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
