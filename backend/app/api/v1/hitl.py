"""HITL review API endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.dependencies import CurrentUserID, DBSession
from app.schemas.common import SuccessResponse
from app.schemas.hitl import (
    HITLReviewResponse,
    ReviewApproveRequest,
    ReviewDecisionResponse,
    ReviewRejectRequest,
    ReviewRevisionRequest,
)
from app.services.hitl_service import HITLService

router = APIRouter()


@router.get("", response_model=SuccessResponse[list[HITLReviewResponse]])
async def list_pending_reviews(db: DBSession):
    """List all pending HITL reviews."""
    service = HITLService(db)
    reviews = await service.list_pending_reviews()
    return SuccessResponse(data=[HITLReviewResponse.model_validate(r) for r in reviews])


@router.get("/{review_id}", response_model=SuccessResponse[HITLReviewResponse])
async def get_review(review_id: UUID, db: DBSession):
    """Get HITL review details."""
    service = HITLService(db)
    review = await service.get_review(review_id)
    return SuccessResponse(data=HITLReviewResponse.model_validate(review))


@router.post("/{review_id}/approve", response_model=SuccessResponse[ReviewDecisionResponse])
async def approve_review(review_id: UUID, data: ReviewApproveRequest, db: DBSession, user_id: CurrentUserID):
    """Approve a HITL review."""
    service = HITLService(db)
    decision = await service.approve_review(review_id, feedback=data.feedback, decided_by=user_id)
    return SuccessResponse(data=ReviewDecisionResponse.model_validate(decision))


@router.post("/{review_id}/reject", response_model=SuccessResponse[ReviewDecisionResponse])
async def reject_review(review_id: UUID, data: ReviewRejectRequest, db: DBSession, user_id: CurrentUserID):
    """Reject a HITL review."""
    service = HITLService(db)
    decision = await service.reject_review(review_id, feedback=data.feedback, decided_by=user_id)
    return SuccessResponse(data=ReviewDecisionResponse.model_validate(decision))


@router.post("/{review_id}/request-revision", response_model=SuccessResponse[ReviewDecisionResponse])
async def request_revision(review_id: UUID, data: ReviewRevisionRequest, db: DBSession, user_id: CurrentUserID):
    """Request revision for a HITL review."""
    service = HITLService(db)
    decision = await service.request_revision(
        review_id, feedback=data.feedback, edits=data.edits, decided_by=user_id
    )
    return SuccessResponse(data=ReviewDecisionResponse.model_validate(decision))
