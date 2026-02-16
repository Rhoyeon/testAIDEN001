"""HITL (Human-in-the-Loop) interrupt management controller."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.orchestration.event_bus import EventBus
from app.orchestration.events import Event, EventTypes
from app.services.hitl_service import HITLService

logger = get_logger("orchestration.hitl")


class HITLController:
    """Manages HITL interrupts: creation, notification, and resolution."""

    def __init__(self, db: AsyncSession, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.hitl_service = HITLService(db)

    async def create_interrupt(
        self,
        execution_id: str,
        project_id: str,
        review_type: str,
        content_snapshot: dict,
        interrupt_id: str | None = None,
    ) -> str:
        """Create a HITL review request and notify via event bus.

        Returns the review ID.
        """
        review = await self.hitl_service.create_review(
            execution_id=uuid.UUID(execution_id),
            task_id=None,
            review_type=review_type,
            content_snapshot=content_snapshot,
            interrupt_id=interrupt_id,
        )

        # Publish HITL requested event
        await self.event_bus.publish_event(Event(
            event_type=EventTypes.HITL_REQUESTED,
            project_id=project_id,
            execution_id=execution_id,
            data={
                "review_id": str(review.id),
                "review_type": review_type,
                "content_snapshot_summary": self._summarize_snapshot(content_snapshot),
            },
        ))

        logger.info(
            f"HITL interrupt created: review_id={review.id}, "
            f"type={review_type}, execution_id={execution_id}"
        )

        return str(review.id)

    async def resolve_interrupt(
        self,
        review_id: str,
        decision: str,
        feedback: str | None = None,
        edits: dict | None = None,
        decided_by: str | None = None,
        project_id: str | None = None,
    ) -> dict:
        """Resolve a HITL interrupt and prepare resume data for the agent.

        Returns the data needed to resume the agent execution.
        """
        review_uuid = uuid.UUID(review_id)

        if decision == "approved":
            await self.hitl_service.approve_review(review_uuid, feedback, decided_by)
        elif decision == "rejected":
            await self.hitl_service.reject_review(review_uuid, feedback or "", decided_by)
        elif decision == "revision_requested":
            await self.hitl_service.request_revision(review_uuid, feedback or "", edits, decided_by)

        # Publish resolution event
        if project_id:
            await self.event_bus.publish_event(Event(
                event_type=EventTypes.HITL_RESOLVED,
                project_id=project_id,
                data={
                    "review_id": review_id,
                    "decision": decision,
                },
            ))

        # Prepare resume data for the agent
        resume_data = {
            "decision": decision,
            "feedback": feedback,
            "edits": edits,
            "decided_by": decided_by,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"HITL interrupt resolved: review_id={review_id}, decision={decision}")

        return resume_data

    def _summarize_snapshot(self, snapshot: dict) -> str:
        """Create a brief summary of the content snapshot for notifications."""
        review_type = snapshot.get("review_type", "unknown")
        message = snapshot.get("message", "Review requested")
        return f"[{review_type}] {message}"
