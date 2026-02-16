"""Deliverable access API endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.dependencies import DBSession
from app.schemas.common import SuccessResponse
from app.schemas.deliverable import DeliverableResponse, DeliverableVersionResponse
from app.services.deliverable_service import DeliverableService

router = APIRouter()


@router.get("/phases/{phase_id}", response_model=SuccessResponse[list[DeliverableResponse]])
async def list_phase_deliverables(phase_id: UUID, db: DBSession):
    """List deliverables for a phase."""
    service = DeliverableService(db)
    deliverables = await service.list_deliverables(phase_id)
    return SuccessResponse(data=[DeliverableResponse.model_validate(d) for d in deliverables])


@router.get("/{deliverable_id}", response_model=SuccessResponse[DeliverableResponse])
async def get_deliverable(deliverable_id: UUID, db: DBSession):
    """Get deliverable details."""
    service = DeliverableService(db)
    deliverable = await service.get_deliverable(deliverable_id)
    return SuccessResponse(data=DeliverableResponse.model_validate(deliverable))


@router.get("/{deliverable_id}/versions", response_model=SuccessResponse[list[DeliverableVersionResponse]])
async def list_deliverable_versions(deliverable_id: UUID, db: DBSession):
    """Get version history for a deliverable."""
    service = DeliverableService(db)
    versions = await service.get_versions(deliverable_id)
    return SuccessResponse(data=[DeliverableVersionResponse.model_validate(v) for v in versions])
