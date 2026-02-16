"""HITL review request/response schemas."""

from __future__ import annotations
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HITLReviewResponse(BaseModel):
    id: UUID
    execution_id: UUID | None
    task_id: UUID | None
    review_type: str
    status: str
    content_snapshot: dict
    reviewer_id: UUID | None
    assigned_at: datetime | None
    decided_at: datetime | None
    deadline_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewApproveRequest(BaseModel):
    feedback: str | None = None


class ReviewRejectRequest(BaseModel):
    feedback: str = Field(..., min_length=1)


class ReviewRevisionRequest(BaseModel):
    feedback: str = Field(..., min_length=1)
    edits: dict = Field(default_factory=dict)


class ReviewDecisionResponse(BaseModel):
    id: UUID
    review_id: UUID
    decision: str
    feedback: str | None
    edits: dict | None
    decided_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
