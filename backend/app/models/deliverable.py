"""Deliverable and DeliverableVersion models."""

from __future__ import annotations
import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import JSONB_COMPAT as JSONB, Base, TimestampMixin, UUIDPrimaryKeyMixin


class Deliverable(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deliverables"

    phase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_phases.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    deliverable_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    format: Mapped[str | None] = mapped_column(String(50))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    phase = relationship("ProjectPhase", back_populates="deliverables")
    versions = relationship(
        "DeliverableVersion", back_populates="deliverable", lazy="selectin",
        order_by="DeliverableVersion.version_number",
    )


class DeliverableVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deliverable_versions"

    deliverable_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_structured: Mapped[dict | None] = mapped_column(JSONB)
    change_summary: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    deliverable = relationship("Deliverable", back_populates="versions")
