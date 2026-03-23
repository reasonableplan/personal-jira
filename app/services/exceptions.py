import uuid


class AgentNotFoundError(Exception):
    def __init__(self, agent_id: uuid.UUID) -> None:
        self.agent_id = agent_id
        super().__init__(f"Agent {agent_id} not found")


class AgentNameConflictError(Exception):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Agent with name '{name}' already exists")


class AgentSkillMismatchError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
