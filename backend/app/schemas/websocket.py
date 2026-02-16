"""WebSocket message schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WSMessage(BaseModel):
    """Server-to-client WebSocket message."""
    type: str
    event: str
    project_id: str
    timestamp: datetime
    data: Any = None


class WSClientMessage(BaseModel):
    """Client-to-server WebSocket message."""
    action: str  # "subscribe" | "unsubscribe" | "ping"
    channel: str | None = None
