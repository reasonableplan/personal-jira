from pydantic import BaseModel


class StatusBreakdown(BaseModel):
    status: str
    count: int


class DashboardStatistics(BaseModel):
    total_issues: int
    status_breakdown: list[StatusBreakdown]
    avg_completion_time_seconds: float | None = None
    review_pass_rate: float | None = None


class AgentStatistics(BaseModel):
    agent_id: str
    total_assigned: int
    total_completed: int
    avg_completion_time_seconds: float | None = None
    rework_count: int = 0
    review_pass_rate: float | None = None
