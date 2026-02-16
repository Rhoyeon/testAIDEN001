"""Event type definitions for the AIDEN orchestration system."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# Event type constants
class EventTypes:
    # Project events
    PROJECT_STARTED = "project.started"
    PROJECT_COMPLETED = "project.completed"
    PROJECT_FAILED = "project.failed"
    PROJECT_PAUSED = "project.paused"

    # Phase events
    PHASE_STARTED = "phase.started"
    PHASE_COMPLETED = "phase.completed"
    PHASE_FAILED = "phase.failed"
    PHASE_TRANSITION = "phase.transition"

    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_NODE_ENTER = "agent.node.enter"
    AGENT_NODE_EXIT = "agent.node.exit"
    AGENT_PROGRESS = "agent.progress"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"

    # HITL events
    HITL_REQUESTED = "agent.hitl.requested"
    HITL_RESOLVED = "agent.hitl.resolved"

    # Deliverable events
    DELIVERABLE_CREATED = "deliverable.created"
    DELIVERABLE_UPDATED = "deliverable.updated"
    DELIVERABLE_APPROVED = "deliverable.approved"


@dataclass
class Event:
    """Structured event for the event bus."""
    event_type: str
    project_id: str
    data: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_id: str | None = None
    agent_name: str | None = None
