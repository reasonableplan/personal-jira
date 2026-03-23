from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.metrics import (
    AgentMetricsResponse,
    IssueMetricsResponse,
    MetricsSummaryResponse,
)
from personal_jira.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


async def get_metrics_service(
    db: AsyncSession = Depends(get_db),
) -> MetricsService:
    return MetricsService(db)


@router.get(
    "/agents/{agent_id}",
    response_model=AgentMetricsResponse,
)
async def get_agent_metrics(
    agent_id: str,
    service: MetricsService = Depends(get_metrics_service),
) -> AgentMetricsResponse:
    metrics = await service.get_agent_metrics(agent_id)
    return AgentMetricsResponse(agent=metrics)


@router.get(
    "/issues/{issue_id}",
    response_model=IssueMetricsResponse,
)
async def get_issue_metrics(
    issue_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
) -> IssueMetricsResponse:
    metrics = await service.get_issue_metrics(str(issue_id))
    if metrics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue {issue_id} not found",
        )
    return IssueMetricsResponse(issue=metrics)


@router.get(
    "/summary",
    response_model=MetricsSummaryResponse,
)
async def get_summary(
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsSummaryResponse:
    summary = await service.get_summary()
    return MetricsSummaryResponse(summary=summary)
