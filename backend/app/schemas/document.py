"""Document request/response schemas."""

from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    doc_type: str
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    is_indexed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    doc_type: str
    file_name: str | None
    file_size: int | None
    mime_type: str | None
    content_text: str | None
    is_indexed: bool
    metadata_: dict = Field(default_factory=dict, alias="metadata_")
    uploaded_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    metadata_: dict = Field(default_factory=dict, alias="metadata_")

    model_config = {"from_attributes": True, "populate_by_name": True}
