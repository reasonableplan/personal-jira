from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_db
from personal_jira.schemas.statistics import AgentStatistics, DashboardStatistics
from personal_jira.services.statistics import StatisticsService

router = APIRouter(prefix="/api/v1/statistics", tags=["statistics"])
statistics_service = StatisticsService()


@router.get("/dashboard", response_model=DashboardStatistics)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
) -> DashboardStatistics:
    return await statistics_service.get_dashboard(db)


@router.get("/agents/{agent_id}", response_model=AgentStatistics)
async def get_agent_statistics(
    agent_id: str, db: AsyncSession = Depends(get_db)
) -> AgentStatistics:
    return await statistics_service.get_agent_stats(db, agent_id)
