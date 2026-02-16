"""Phase management API endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.dependencies import DBSession
from app.schemas.common import SuccessResponse
from app.schemas.project import PhaseResponse, PhaseStatusResponse
from app.services.phase_service import PhaseService

router = APIRouter()


@router.get("/projects/{project_id}", response_model=SuccessResponse[list[PhaseResponse]])
async def list_project_phases(project_id: UUID, db: DBSession):
    """List all phases for a project."""
    service = PhaseService(db)
    phases = await service.get_phases_for_project(project_id)
    return SuccessResponse(data=[PhaseResponse.model_validate(p) for p in phases])


@router.get("/{phase_id}", response_model=SuccessResponse[PhaseResponse])
async def get_phase(phase_id: UUID, db: DBSession):
    """Get phase details."""
    service = PhaseService(db)
    phase = await service.get_phase(phase_id)
    return SuccessResponse(data=PhaseResponse.model_validate(phase))


@router.get("/{phase_id}/status", response_model=SuccessResponse[PhaseStatusResponse])
async def get_phase_status(phase_id: UUID, db: DBSession):
    """Get phase status with progress information."""
    service = PhaseService(db)
    phase = await service.get_phase(phase_id)
    return SuccessResponse(
        data=PhaseStatusResponse(
            id=phase.id,
            phase_type=phase.phase_type,
            status=phase.status,
            agent_name=phase.agent_name,
            progress={},
        )
    )


@router.post("/{phase_id}/start", response_model=SuccessResponse[PhaseResponse])
async def start_phase(phase_id: UUID, db: DBSession):
    """Start a specific phase."""
    service = PhaseService(db)
    phase = await service.start_phase(phase_id)
    return SuccessResponse(data=PhaseResponse.model_validate(phase))
