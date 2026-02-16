"""Project business logic service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.project import Project, ProjectPhase
from app.schemas.project import ProjectCreate, ProjectUpdate

# Default phase configuration
DEFAULT_PHASES = [
    {"phase_type": "analysis", "phase_order": 1, "agent_name": "ryan"},
    {"phase_type": "design", "phase_order": 2, "agent_name": None},
    {"phase_type": "development", "phase_order": 3, "agent_name": None},
    {"phase_type": "testing", "phase_order": 4, "agent_name": None},
]


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate, owner_id: str | None = None) -> Project:
        """Create a new project with default phases."""
        project = Project(
            name=data.name,
            description=data.description,
            config=data.config,
            owner_id=uuid.UUID(owner_id) if owner_id else None,
            status="created",
        )
        self.db.add(project)
        await self.db.flush()

        # Create default phases
        for phase_def in DEFAULT_PHASES:
            phase = ProjectPhase(
                project_id=project.id,
                phase_type=phase_def["phase_type"],
                phase_order=phase_def["phase_order"],
                agent_name=phase_def["agent_name"],
                status="pending",
            )
            self.db.add(phase)

        await self.db.flush()
        return project

    async def get_project(self, project_id: uuid.UUID) -> Project:
        """Get a project by ID with all relationships loaded."""
        stmt = (
            select(Project)
            .options(selectinload(Project.phases))
            .where(Project.id == project_id)
        )
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError("Project", str(project_id))
        return project

    async def list_projects(self, offset: int = 0, limit: int = 20) -> tuple[list[Project], int]:
        """List projects with pagination."""
        # Count
        count_stmt = select(Project)
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Fetch
        stmt = (
            select(Project)
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        projects = list(result.scalars().all())
        return projects, total

    async def update_project(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
        """Update a project."""
        project = await self.get_project(project_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        project.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return project

    async def delete_project(self, project_id: uuid.UUID) -> None:
        """Soft delete a project by setting status to 'archived'."""
        project = await self.get_project(project_id)
        project.status = "archived"
        project.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def start_project(self, project_id: uuid.UUID) -> Project:
        """Start a project workflow - transitions to analysis phase."""
        project = await self.get_project(project_id)
        if project.status not in ("created", "paused"):
            raise ValueError(f"Cannot start project in status: {project.status}")

        project.status = "analysis"
        project.current_phase = "analysis"
        project.updated_at = datetime.now(timezone.utc)

        # Update first phase status
        for phase in project.phases:
            if phase.phase_type == "analysis":
                phase.status = "ready"
                break

        await self.db.flush()
        return project
