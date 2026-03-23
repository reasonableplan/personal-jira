from sqlalchemy import case, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue
from personal_jira.schemas.statistics import (
    AgentStatistics,
    DashboardStatistics,
    StatusBreakdown,
)

STATUS_DONE = "done"


class StatisticsService:
    async def get_dashboard(self, db: AsyncSession) -> DashboardStatistics:
        total_result = await db.execute(select(func.count(Issue.id)))
        total_issues = total_result.scalar_one()

        status_result = await db.execute(
            select(Issue.status, func.count(Issue.id)).group_by(Issue.status)
        )
        breakdown = [
            StatusBreakdown(status=row[0], count=row[1])
            for row in status_result.all()
        ]

        avg_result = await db.execute(
            select(
                func.avg(
                    extract("epoch", Issue.updated_at - Issue.created_at)
                )
            ).where(Issue.status == STATUS_DONE)
        )
        avg_time = avg_result.scalar_one()

        review_result = await db.execute(
            select(
                func.avg(
                    case(
                        (Issue.status == STATUS_DONE, 1.0),
                        else_=0.0,
                    )
                )
            ).where(Issue.status.in_([STATUS_DONE, "rejected"]))
        )
        review_rate = review_result.scalar_one()

        return DashboardStatistics(
            total_issues=total_issues,
            status_breakdown=breakdown,
            avg_completion_time_seconds=avg_time,
            review_pass_rate=review_rate,
        )

    async def get_agent_stats(
        self, db: AsyncSession, agent_id: str
    ) -> AgentStatistics:
        total_result = await db.execute(
            select(func.count(Issue.id)).where(Issue.assignee == agent_id)
        )
        total_assigned = total_result.scalar_one()

        completed_result = await db.execute(
            select(func.count(Issue.id)).where(
                Issue.assignee == agent_id, Issue.status == STATUS_DONE
            )
        )
        total_completed = completed_result.scalar_one()

        avg_result = await db.execute(
            select(
                func.avg(
                    extract("epoch", Issue.updated_at - Issue.created_at)
                )
            ).where(Issue.assignee == agent_id, Issue.status == STATUS_DONE)
        )
        avg_time = avg_result.scalar_one()

        rework_result = await db.execute(
            select(func.coalesce(func.sum(Issue.rework_count), 0)).where(
                Issue.assignee == agent_id
            )
        )
        rework_count = rework_result.scalar_one()

        review_result = await db.execute(
            select(
                func.avg(
                    case(
                        (Issue.status == STATUS_DONE, 1.0),
                        else_=0.0,
                    )
                )
            ).where(
                Issue.assignee == agent_id,
                Issue.status.in_([STATUS_DONE, "rejected"]),
            )
        )
        review_rate = review_result.scalar_one()

        return AgentStatistics(
            agent_id=agent_id,
            total_assigned=total_assigned,
            total_completed=total_completed,
            avg_completion_time_seconds=avg_time,
            rework_count=rework_count,
            review_pass_rate=review_rate,
        )
