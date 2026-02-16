"""Deliverable management service."""

from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.deliverable import Deliverable, DeliverableVersion


class DeliverableService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_deliverable(
        self,
        phase_id: uuid.UUID,
        title: str,
        deliverable_type: str,
        content: str,
        content_structured: dict | None = None,
        format: str = "markdown",
        created_by: str = "system",
    ) -> Deliverable:
        """Create a new deliverable with its first version."""
        deliverable = Deliverable(
            phase_id=phase_id,
            title=title,
            deliverable_type=deliverable_type,
            status="draft",
            current_version=1,
            format=format,
        )
        self.db.add(deliverable)
        await self.db.flush()

        # Create first version
        version = DeliverableVersion(
            deliverable_id=deliverable.id,
            version_number=1,
            content=content,
            content_structured=content_structured,
            change_summary="Initial version",
            created_by=created_by,
        )
        self.db.add(version)
        await self.db.flush()
        return deliverable

    async def get_deliverable(self, deliverable_id: uuid.UUID) -> Deliverable:
        """Get a deliverable by ID."""
        stmt = select(Deliverable).where(Deliverable.id == deliverable_id)
        result = await self.db.execute(stmt)
        deliverable = result.scalar_one_or_none()
        if not deliverable:
            raise NotFoundError("Deliverable", str(deliverable_id))
        return deliverable

    async def list_deliverables(self, phase_id: uuid.UUID) -> list[Deliverable]:
        """List deliverables for a phase."""
        stmt = (
            select(Deliverable)
            .where(Deliverable.phase_id == phase_id)
            .order_by(Deliverable.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def add_version(
        self,
        deliverable_id: uuid.UUID,
        content: str,
        content_structured: dict | None = None,
        change_summary: str | None = None,
        created_by: str = "system",
    ) -> DeliverableVersion:
        """Add a new version to an existing deliverable."""
        deliverable = await self.get_deliverable(deliverable_id)
        new_version_number = deliverable.current_version + 1

        version = DeliverableVersion(
            deliverable_id=deliverable.id,
            version_number=new_version_number,
            content=content,
            content_structured=content_structured,
            change_summary=change_summary,
            created_by=created_by,
        )
        self.db.add(version)

        deliverable.current_version = new_version_number
        await self.db.flush()
        return version

    async def get_versions(self, deliverable_id: uuid.UUID) -> list[DeliverableVersion]:
        """Get all versions of a deliverable."""
        stmt = (
            select(DeliverableVersion)
            .where(DeliverableVersion.deliverable_id == deliverable_id)
            .order_by(DeliverableVersion.version_number)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def approve_deliverable(self, deliverable_id: uuid.UUID) -> Deliverable:
        """Mark deliverable as approved/final."""
        deliverable = await self.get_deliverable(deliverable_id)
        deliverable.status = "approved"
        await self.db.flush()
        return deliverable
