from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Self


class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class AgentMetrics(BaseModel):
    agent_id: str
    total_tasks: int = Field(ge=0)
    completed_tasks: int = Field(ge=0)
    failed_tasks: int = Field(ge=0)
    review_pass_rate: float = Field(ge=0.0, le=1.0)
    rework_count: int = Field(ge=0)
    avg_completion_seconds: float = Field(ge=0.0)
    total_work_seconds: float = Field(ge=0.0)


class IssueMetrics(BaseModel):
    issue_id: str
    title: str
    status: str
    assigned_agent: str | None
    review_attempts: int = Field(ge=0)
    rework_count: int = Field(ge=0)
    total_work_seconds: float = Field(ge=0.0)
    elapsed_seconds: float = Field(ge=0.0)


class MetricsSummary(BaseModel):
    total_issues: int = Field(ge=0)
    completed_issues: int = Field(ge=0)
    in_progress_issues: int = Field(ge=0)
    blocked_issues: int = Field(ge=0)
    overall_review_pass_rate: float = Field(ge=0.0, le=1.0)
    overall_avg_completion_seconds: float = Field(ge=0.0)
    total_rework_count: int = Field(ge=0)
    active_agents: int = Field(ge=0)


class AgentMetricsResponse(BaseModel):
    agent: AgentMetrics


class IssueMetricsResponse(BaseModel):
    issue: IssueMetrics


class MetricsSummaryResponse(BaseModel):
    summary: MetricsSummary
