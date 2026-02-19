"""Project and ProjectPhase models."""

from __future__ import annotations
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import JSONB_COMPAT as JSONB, Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="created", index=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    current_phase: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    owner = relationship("User", back_populates="projects", lazy="selectin")
    phases = relationship(
        "ProjectPhase", back_populates="project", lazy="selectin",
        order_by="ProjectPhase.phase_order",
    )
    documents = relationship("Document", back_populates="project", lazy="selectin")


class ProjectPhase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "project_phases"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    phase_type: Mapped[str] = mapped_column(String(50), nullable=False)
    phase_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    agent_name: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    project = relationship("Project", back_populates="phases")
    tasks = relationship("Task", back_populates="phase", lazy="selectin")
    deliverables = relationship("Deliverable", back_populates="phase", lazy="selectin")
    executions = relationship("AgentExecution", back_populates="phase", lazy="selectin")
