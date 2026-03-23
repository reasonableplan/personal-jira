from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from personal_jira.database import get_session_factory
from personal_jira.websocket.connection_manager import ConnectionManager

_connection_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session
