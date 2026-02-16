"""Deliverable request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeliverableResponse(BaseModel):
    id: UUID
    phase_id: UUID
    title: str
    deliverable_type: str
    status: str
    current_version: int
    format: str | None
    metadata_: dict = Field(default_factory=dict, alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class DeliverableVersionResponse(BaseModel):
    id: UUID
    deliverable_id: UUID
    version_number: int
    content: str
    content_structured: dict | None
    change_summary: str | None
    created_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeliverableExportRequest(BaseModel):
    format: str = Field(default="markdown", pattern="^(markdown|html|pdf|docx)$")
