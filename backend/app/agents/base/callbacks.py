"""Agent lifecycle callbacks for event emission and logging."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

logger = get_logger("agents.callbacks")


class AgentEventEmitter:
    """Emits agent lifecycle events to the event bus."""

    def __init__(self, agent_name: str, execution_id: str, project_id: str, event_bus: Any = None):
        self.agent_name = agent_name
        self.execution_id = execution_id
        self.project_id = project_id
        self.event_bus = event_bus

    async def emit(self, event_type: str, data: dict | None = None) -> None:
        """Emit an event through the event bus."""
        event = {
            "event_type": event_type,
            "agent_name": self.agent_name,
            "execution_id": self.execution_id,
            "project_id": self.project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        }

        logger.debug(f"Event: {event_type} | agent={self.agent_name}")

        if self.event_bus:
            try:
                await self.event_bus.publish(event_type=event_type, data=event)
            except Exception as e:
                logger.warning(f"Failed to emit event {event_type}: {e}")

    async def node_started(self, node_name: str) -> None:
        await self.emit("agent.node.enter", {"node_name": node_name})

    async def node_completed(self, node_name: str, duration_ms: int | None = None) -> None:
        await self.emit("agent.node.exit", {"node_name": node_name, "duration_ms": duration_ms})

    async def hitl_requested(self, review_type: str, content_snapshot: dict) -> None:
        await self.emit("agent.hitl.requested", {
            "review_type": review_type,
            "content_snapshot": content_snapshot,
        })

    async def agent_completed(self, deliverables: list | None = None) -> None:
        await self.emit("agent.completed", {"deliverables": deliverables or []})

    async def agent_error(self, error: str) -> None:
        await self.emit("agent.error", {"error": error})
