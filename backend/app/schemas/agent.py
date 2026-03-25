from datetime import datetime

from pydantic import BaseModel


class AgentCreate(BaseModel):
    id: str
    name: str
    domain: str


class AgentUpdate(BaseModel):
    status: str | None = None


class AgentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    domain: str
    status: str
    last_heartbeat: datetime | str | None = None
