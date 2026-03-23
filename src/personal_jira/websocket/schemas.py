from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class WSMessageType(StrEnum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"


class SubscribePayload(BaseModel):
    channel: str


class UnsubscribePayload(BaseModel):
    channel: str


class WSMessage(BaseModel):
    type: WSMessageType
    payload: Any = {}
