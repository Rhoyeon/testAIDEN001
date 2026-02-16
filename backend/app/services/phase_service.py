"""Phase management service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.project import ProjectPhase


class PhaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_phase(self, phase_id: uuid.UUID) -> ProjectPhase:
        """Get a phase by ID."""
        stmt = select(ProjectPhase).where(ProjectPhase.id == phase_id)
        result = await self.db.execute(stmt)
        phase = result.scalar_one_or_none()
        if not phase:
            raise NotFoundError("Phase", str(phase_id))
        return phase

    async def get_phases_for_project(self, project_id: uuid.UUID) -> list[ProjectPhase]:
        """Get all phases for a project ordered by phase_order."""
        stmt = (
            select(ProjectPhase)
            .where(ProjectPhase.project_id == project_id)
            .order_by(ProjectPhase.phase_order)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def start_phase(self, phase_id: uuid.UUID) -> ProjectPhase:
        """Start a phase execution."""
        phase = await self.get_phase(phase_id)
        if phase.status not in ("pending", "ready"):
            raise ValueError(f"Cannot start phase in status: {phase.status}")

        phase.status = "in_progress"
        phase.started_at = datetime.now(timezone.utc)
        await self.db.flush()
        return phase

    async def complete_phase(self, phase_id: uuid.UUID) -> ProjectPhase:
        """Mark a phase as completed."""
        phase = await self.get_phase(phase_id)
        phase.status = "completed"
        phase.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return phase

    async def fail_phase(self, phase_id: uuid.UUID) -> ProjectPhase:
        """Mark a phase as failed."""
        phase = await self.get_phase(phase_id)
        phase.status = "failed"
        await self.db.flush()
        return phase

    async def set_hitl_review(self, phase_id: uuid.UUID) -> ProjectPhase:
        """Set phase to HITL review status."""
        phase = await self.get_phase(phase_id)
        phase.status = "hitl_review"
        await self.db.flush()
        return phase
