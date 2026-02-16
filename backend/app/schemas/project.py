"""Project and Phase request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --- Project Schemas ---

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    config: dict = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    config: dict | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    owner_id: UUID | None
    config: dict
    current_phase: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(ProjectResponse):
    """Lightweight project response for list views."""
    pass


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with related data."""
    phases: list["PhaseResponse"] = []


# --- Phase Schemas ---

class PhaseResponse(BaseModel):
    id: UUID
    project_id: UUID
    phase_type: str
    phase_order: int
    status: str
    agent_name: str | None
    started_at: datetime | None
    completed_at: datetime | None
    config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PhaseStatusResponse(BaseModel):
    """Phase status with progress details."""
    id: UUID
    phase_type: str
    status: str
    agent_name: str | None
    progress: dict = Field(default_factory=dict)


# Rebuild forward refs
ProjectDetailResponse.model_rebuild()
