"""HITL Review and ReviewDecision models."""

from __future__ import annotations
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import JSONB_COMPAT as JSONB, Base, TimestampMixin, UUIDPrimaryKeyMixin


class HITLReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hitl_reviews"

    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_executions.id"), nullable=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )
    review_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    interrupt_id: Mapped[str | None] = mapped_column(String(255))
    content_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    decisions = relationship("ReviewDecision", back_populates="review", lazy="selectin")


class ReviewDecision(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "review_decisions"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hitl_reviews.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text)
    edits: Mapped[dict | None] = mapped_column(JSONB)
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    # Relationships
    review = relationship("HITLReview", back_populates="decisions")
