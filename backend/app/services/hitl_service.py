"""HITL review management service."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.hitl import HITLReview, ReviewDecision


class HITLService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(
        self,
        execution_id: uuid.UUID | None,
        task_id: uuid.UUID | None,
        review_type: str,
        content_snapshot: dict,
        interrupt_id: str | None = None,
    ) -> HITLReview:
        """Create a new HITL review request."""
        review = HITLReview(
            execution_id=execution_id,
            task_id=task_id,
            review_type=review_type,
            status="pending",
            content_snapshot=content_snapshot,
            interrupt_id=interrupt_id,
        )
        self.db.add(review)
        await self.db.flush()
        return review

    async def get_review(self, review_id: uuid.UUID) -> HITLReview:
        """Get a review by ID."""
        stmt = select(HITLReview).where(HITLReview.id == review_id)
        result = await self.db.execute(stmt)
        review = result.scalar_one_or_none()
        if not review:
            raise NotFoundError("HITLReview", str(review_id))
        return review

    async def list_pending_reviews(self) -> list[HITLReview]:
        """List all pending HITL reviews."""
        stmt = (
            select(HITLReview)
            .where(HITLReview.status.in_(["pending", "in_review"]))
            .order_by(HITLReview.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def approve_review(
        self, review_id: uuid.UUID, feedback: str | None = None, decided_by: str | None = None
    ) -> ReviewDecision:
        """Approve a HITL review."""
        review = await self.get_review(review_id)
        review.status = "approved"
        review.decided_at = datetime.now(timezone.utc)

        decision = ReviewDecision(
            review_id=review.id,
            decision="approved",
            feedback=feedback,
            decided_by=uuid.UUID(decided_by) if decided_by else None,
        )
        self.db.add(decision)
        await self.db.flush()
        return decision

    async def reject_review(
        self, review_id: uuid.UUID, feedback: str, decided_by: str | None = None
    ) -> ReviewDecision:
        """Reject a HITL review."""
        review = await self.get_review(review_id)
        review.status = "rejected"
        review.decided_at = datetime.now(timezone.utc)

        decision = ReviewDecision(
            review_id=review.id,
            decision="rejected",
            feedback=feedback,
            decided_by=uuid.UUID(decided_by) if decided_by else None,
        )
        self.db.add(decision)
        await self.db.flush()
        return decision

    async def request_revision(
        self,
        review_id: uuid.UUID,
        feedback: str,
        edits: dict | None = None,
        decided_by: str | None = None,
    ) -> ReviewDecision:
        """Request revision for a HITL review."""
        review = await self.get_review(review_id)
        review.status = "revision_requested"
        review.decided_at = datetime.now(timezone.utc)

        decision = ReviewDecision(
            review_id=review.id,
            decision="revision_requested",
            feedback=feedback,
            edits=edits,
            decided_by=uuid.UUID(decided_by) if decided_by else None,
        )
        self.db.add(decision)
        await self.db.flush()
        return decision
