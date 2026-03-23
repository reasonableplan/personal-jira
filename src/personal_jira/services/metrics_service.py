from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.models.work_log import WorkLog
from personal_jira.schemas.metrics import AgentMetrics, IssueMetrics, MetricsSummary


class MetricsService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        result = await self._db.execute(
            select(Issue).where(Issue.assigned_to == agent_id)
        )
        issues = result.scalars().all()

        if not issues:
            return AgentMetrics(
                agent_id=agent_id,
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                review_pass_rate=0.0,
                rework_count=0,
                avg_completion_seconds=0.0,
                total_work_seconds=0.0,
            )

        wl_result = await self._db.execute(
            select(WorkLog).where(WorkLog.agent_id == agent_id)
        )
        worklogs = wl_result.scalars().all()

        completed = [i for i in issues if i.status == IssueStatus.DONE]
        failed = [i for i in issues if i.status == IssueStatus.FAILED]
        total_reviews = sum(i.review_count for i in completed)
        total_reworks = sum(i.rework_count for i in issues)
        total_work_secs = sum(wl.duration_seconds for wl in worklogs)

        review_pass_rate = 0.0
        if total_reviews > 0:
            review_pass_rate = (total_reviews - total_reworks) / total_reviews

        avg_completion = _calc_avg_completion(completed)

        return AgentMetrics(
            agent_id=agent_id,
            total_tasks=len(issues),
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            review_pass_rate=round(review_pass_rate, 4),
            rework_count=total_reworks,
            avg_completion_seconds=avg_completion,
            total_work_seconds=total_work_secs,
        )

    async def get_issue_metrics(self, issue_id: str) -> IssueMetrics | None:
        result = await self._db.execute(
            select(Issue).where(Issue.id == issue_id)
        )
        issue = result.scalar_one_or_none()
        if issue is None:
            return None

        wl_result = await self._db.execute(
            select(WorkLog).where(WorkLog.issue_id == issue_id)
        )
        worklogs = wl_result.scalars().all()
        total_work_secs = sum(wl.duration_seconds for wl in worklogs)

        elapsed = (issue.updated_at - issue.created_at).total_seconds()

        return IssueMetrics(
            issue_id=str(issue.id),
            title=issue.title,
            status=issue.status.value if hasattr(issue.status, "value") else str(issue.status),
            assigned_agent=issue.assigned_to,
            review_attempts=issue.review_count,
            rework_count=issue.rework_count,
            total_work_seconds=total_work_secs,
            elapsed_seconds=elapsed,
        )

    async def get_summary(self) -> MetricsSummary:
        result = await self._db.execute(select(Issue))
        issues = result.scalars().all()

        if not issues:
            return MetricsSummary(
                total_issues=0,
                completed_issues=0,
                in_progress_issues=0,
                blocked_issues=0,
                overall_review_pass_rate=0.0,
                overall_avg_completion_seconds=0.0,
                total_rework_count=0,
                active_agents=0,
            )

        completed = [i for i in issues if i.status == IssueStatus.DONE]
        in_progress = [i for i in issues if i.status == IssueStatus.IN_PROGRESS]
        blocked = [i for i in issues if i.status == IssueStatus.BLOCKED]

        total_reviews = sum(i.review_count for i in completed)
        total_reworks = sum(i.rework_count for i in issues)

        review_pass_rate = 0.0
        if total_reviews > 0:
            review_pass_rate = (total_reviews - total_reworks) / total_reviews

        avg_completion = _calc_avg_completion(completed)

        agents = {i.assigned_to for i in issues if i.assigned_to is not None}

        return MetricsSummary(
            total_issues=len(issues),
            completed_issues=len(completed),
            in_progress_issues=len(in_progress),
            blocked_issues=len(blocked),
            overall_review_pass_rate=round(review_pass_rate, 4),
            overall_avg_completion_seconds=avg_completion,
            total_rework_count=total_reworks,
            active_agents=len(agents),
        )


def _calc_avg_completion(completed: list) -> float:
    if not completed:
        return 0.0
    total = sum(
        (i.updated_at - i.created_at).total_seconds()
        for i in completed
    )
    return round(total / len(completed), 2)
