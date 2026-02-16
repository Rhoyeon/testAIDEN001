"""AgentExecution and AgentLog models."""

from __future__ import annotations
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentExecution(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_executions"

    phase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_phases.id", ondelete="CASCADE"), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    thread_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="initialized", index=True)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Relationships
    phase = relationship("ProjectPhase", back_populates="executions")
    logs = relationship("AgentLog", back_populates="execution", lazy="dynamic")


class AgentLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "agent_logs"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_executions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    log_level: Mapped[str] = mapped_column(String(20), nullable=False)
    node_name: Mapped[str | None] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False, index=True
    )

    # Relationships
    execution = relationship("AgentExecution", back_populates="logs")
