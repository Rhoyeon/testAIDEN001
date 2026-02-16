"""Agent execution request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgentExecutionResponse(BaseModel):
    id: UUID
    phase_id: UUID
    agent_name: str
    thread_id: str
    status: str
    config: dict
    total_tokens: int
    total_cost: float
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentLogResponse(BaseModel):
    id: UUID
    execution_id: UUID
    log_level: str
    node_name: str | None
    event_type: str
    message: str
    data: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentStepResponse(BaseModel):
    """Simplified step view for agent progress tracking."""
    step_name: str
    step_order: int
    status: str
    duration_ms: int | None
    started_at: datetime | None
    completed_at: datetime | None
