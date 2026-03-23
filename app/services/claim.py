from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, AgentStatus
from app.models.issue import Issue, IssueStatus
from app.schemas.claim import ClaimRequest
from app.services.exceptions import AgentNotFoundError, AgentSkillMismatchError


class ClaimService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @staticmethod
    def skills_satisfied(agent_skills: list[str], required_skills: list[str]) -> bool:
        if not required_skills:
            return True
        return set(required_skills).issubset(set(agent_skills))

    async def claim(self, req: ClaimRequest) -> Issue | None:
        agent_stmt = select(Agent).where(Agent.id == req.agent_id)
        result = await self._db.execute(agent_stmt)
        agent = result.scalar_one_or_none()
        if not agent:
            raise AgentNotFoundError(req.agent_id)

        if agent.status == AgentStatus.BUSY:
            raise AgentSkillMismatchError(f"Agent {agent.name} is busy")

        issue_stmt = (
            select(Issue)
            .where(Issue.status == IssueStatus.READY)
            .with_for_update(skip_locked=True)
            .order_by(Issue.created_at.asc())
        )
        if agent.skills:
            issue_stmt = issue_stmt.where(
                Issue.required_skills.contained_by(agent.skills)
            )

        result = await self._db.execute(issue_stmt)
        issue = result.scalar_one_or_none()
        if not issue:
            return None

        issue.status = IssueStatus.IN_PROGRESS
        issue.assignee = agent.name
        agent.status = AgentStatus.BUSY
        agent.current_issue_id = issue.id

        await self._db.commit()
        await self._db.refresh(issue)
        return issue
