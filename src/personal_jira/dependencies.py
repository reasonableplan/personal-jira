from personal_jira.services.connection_manager import ConnectionManager
from personal_jira.services.event_broadcaster import EventBroadcaster

_connection_manager: ConnectionManager | None = None
_event_broadcaster: EventBroadcaster | None = None


def get_connection_manager() -> ConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_event_broadcaster() -> EventBroadcaster:
    global _event_broadcaster
    if _event_broadcaster is None:
        _event_broadcaster = EventBroadcaster(manager=get_connection_manager())
    return _event_broadcaster


def reset_singletons() -> None:
    global _connection_manager, _event_broadcaster
    _connection_manager = None
    _event_broadcaster = None
