import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.exceptions import AgentNotFoundError, AgentNameConflictError


class AgentService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, req: AgentCreate) -> Agent:
        stmt = select(Agent).where(Agent.name == req.name)
        result = await self._db.execute(stmt)
        if result.scalar_one_or_none():
            raise AgentNameConflictError(req.name)

        agent = Agent(name=req.name, skills=req.skills)
        self._db.add(agent)
        await self._db.commit()
        await self._db.refresh(agent)
        return agent

    async def get(self, agent_id: uuid.UUID) -> Agent:
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await self._db.execute(stmt)
        agent = result.scalar_one_or_none()
        if not agent:
            raise AgentNotFoundError(agent_id)
        return agent

    async def list(self, status: Optional[AgentStatus] = None) -> list[Agent]:
        stmt = select(Agent)
        if status:
            stmt = stmt.where(Agent.status == status)
        stmt = stmt.order_by(Agent.created_at.desc())
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, agent_id: uuid.UUID, req: AgentUpdate) -> Agent:
        agent = await self.get(agent_id)
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        await self._db.commit()
        await self._db.refresh(agent)
        return agent

    async def delete(self, agent_id: uuid.UUID) -> None:
        agent = await self.get(agent_id)
        await self._db.delete(agent)
        await self._db.commit()
