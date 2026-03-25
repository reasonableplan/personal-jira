from datetime import UTC, datetime, timedelta

from app.database import get_session
from app.exceptions import ConflictError, NotFoundError
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

STALE_HEARTBEAT_MINUTES = 5

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _to_response(agent: Agent, check_stale: bool = False) -> AgentResponse:
    agent_status = agent.status
    if (
        check_stale
        and agent.last_heartbeat is not None
        and agent.status != "offline"
    ):
        heartbeat = agent.last_heartbeat
        if heartbeat.tzinfo is None:
            heartbeat = heartbeat.replace(tzinfo=UTC)
        if datetime.now(UTC) - heartbeat > timedelta(minutes=STALE_HEARTBEAT_MINUTES):
            agent_status = "offline"
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        domain=agent.domain,
        status=agent_status,
        last_heartbeat=agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreate,
    session: AsyncSession = Depends(get_session),
) -> AgentResponse:
    result = await session.execute(select(Agent).where(Agent.id == body.id))
    if result.scalar_one_or_none() is not None:
        raise ConflictError(f"Agent '{body.id}' already exists")
    agent = Agent(id=body.id, name=body.name, domain=body.domain)
    session.add(agent)
    await session.commit()
    refreshed = await session.get(Agent, body.id)
    return _to_response(refreshed)


@router.get("/")
async def list_agents(
    status_filter: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[AgentResponse]:
    stmt = select(Agent)
    if status_filter is not None:
        stmt = stmt.where(Agent.status == status_filter)
    result = await session.execute(stmt)
    agents = result.scalars().all()
    return [_to_response(a, check_stale=True) for a in agents]


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    session: AsyncSession = Depends(get_session),
) -> AgentResponse:
    agent = await session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' not found")
    return _to_response(agent, check_stale=True)


@router.patch("/{agent_id}/heartbeat")
async def heartbeat(
    agent_id: str,
    body: AgentUpdate | None = None,
    session: AsyncSession = Depends(get_session),
) -> AgentResponse:
    agent = await session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError(f"Agent '{agent_id}' not found")
    agent.last_heartbeat = datetime.now(UTC)  # type: ignore[assignment]
    if body and body.status is not None:
        agent.status = body.status  # type: ignore[assignment]
    await session.commit()
    await session.refresh(agent)
    return _to_response(agent)
