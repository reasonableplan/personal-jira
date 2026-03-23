import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import AgentStatus
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.services.agent import AgentService
from app.services.exceptions import AgentNotFoundError, AgentNameConflictError

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AgentResponse)
async def create_agent(req: AgentCreate, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    try:
        agent = await svc.create(req)
    except AgentNameConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    try:
        return await svc.get(agent_id)
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    status_filter: Optional[AgentStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    svc = AgentService(db)
    return await svc.list(status=status_filter)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    req: AgentUpdate,
    db: AsyncSession = Depends(get_db),
):
    svc = AgentService(db)
    try:
        return await svc.update(agent_id, req)
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = AgentService(db)
    try:
        await svc.delete(agent_id)
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
