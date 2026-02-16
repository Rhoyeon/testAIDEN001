"""Orchestration Engine - Central coordinator for AIDEN project workflows.

The engine manages the lifecycle of projects, phases, and agent executions.
It dispatches agents, handles phase transitions, and coordinates HITL reviews.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import get_agent_class
from app.agents.base.agent import BaseAgent
from app.core.exceptions import AgentExecutionError, NotFoundError
from app.core.logging import get_logger
from app.llm.provider import LLMProvider
from app.models.agent import AgentExecution
from app.models.deliverable import Deliverable, DeliverableVersion
from app.models.project import Project, ProjectPhase
from app.orchestration.event_bus import EventBus
from app.orchestration.events import Event, EventTypes
from app.orchestration.hitl_controller import HITLController
from app.orchestration.phase_controller import PhaseController
from app.rag.pipeline import RAGPipeline
from app.services.deliverable_service import DeliverableService

logger = get_logger("orchestration.engine")


class OrchestrationEngine:
    """Central coordinator for AIDEN project workflows.

    Responsibilities:
    - Initialize and start projects
    - Dispatch agents for each phase
    - Handle phase transitions
    - Coordinate HITL reviews
    - Persist deliverables from agent outputs
    """

    def __init__(
        self,
        db: AsyncSession,
        llm_provider: LLMProvider,
        rag_pipeline: RAGPipeline,
        event_bus: EventBus,
    ):
        self.db = db
        self.llm_provider = llm_provider
        self.rag_pipeline = rag_pipeline
        self.event_bus = event_bus
        self.phase_controller = PhaseController()
        self.hitl_controller = HITLController(db, event_bus)
        self.deliverable_service = DeliverableService(db)

    async def start_project(self, project_id: str) -> dict:
        """Start a project workflow - begins with the first phase."""
        project = await self._get_project(project_id)

        if project.status not in ("created", "paused"):
            raise ValueError(f"Cannot start project in status: {project.status}")

        # Update project status
        project.status = "analysis"
        project.current_phase = "analysis"

        # Publish event
        await self.event_bus.publish_event(Event(
            event_type=EventTypes.PROJECT_STARTED,
            project_id=project_id,
        ))

        # Start first phase
        first_phase = next((p for p in project.phases if p.phase_type == "analysis"), None)
        if first_phase:
            await self.start_phase(project_id, str(first_phase.id))

        await self.db.flush()

        logger.info(f"Project started: {project_id}")
        return {"project_id": project_id, "status": "analysis", "phase": "analysis"}

    async def start_phase(self, project_id: str, phase_id: str) -> dict:
        """Dispatch the appropriate agent for a phase."""
        phase = await self._get_phase(phase_id)

        if not PhaseController.is_phase_ready(phase.phase_type):
            raise ValueError(f"Phase '{phase.phase_type}' has no agent assigned yet")

        # Update phase status
        phase.status = "in_progress"
        phase.started_at = datetime.now(timezone.utc)

        # Create agent execution record
        thread_id = f"aiden_{project_id}_{phase.phase_type}_{uuid.uuid4().hex[:8]}"
        execution = AgentExecution(
            phase_id=phase.id,
            agent_name=PhaseController.get_agent_for_phase(phase.phase_type),
            thread_id=thread_id,
            status="initialized",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(execution)
        await self.db.flush()

        # Publish event
        await self.event_bus.publish_event(Event(
            event_type=EventTypes.PHASE_STARTED,
            project_id=project_id,
            execution_id=str(execution.id),
            agent_name=execution.agent_name,
            data={"phase_type": phase.phase_type},
        ))

        # Instantiate and run agent
        try:
            agent_class = get_agent_class(phase.phase_type)
            agent = agent_class(
                llm_provider=self.llm_provider,
                rag_pipeline=self.rag_pipeline,
                event_bus=self.event_bus,
            )
            await agent.compile()

            # Prepare input data
            input_data = await self._prepare_phase_input(project_id, phase, str(execution.id))

            # Execute agent
            execution.status = "running"
            await self.db.flush()

            result = await agent.execute(
                input_data=input_data,
                thread_id=thread_id,
            )

            # Handle completion
            await self._handle_agent_completion(execution, phase, result)

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            phase.status = "failed"
            await self.db.flush()

            await self.event_bus.publish_event(Event(
                event_type=EventTypes.AGENT_ERROR,
                project_id=project_id,
                execution_id=str(execution.id),
                agent_name=execution.agent_name,
                data={"error": str(e)},
            ))

            logger.error(f"Agent execution failed: {e}")
            raise AgentExecutionError(execution.agent_name, str(e))

        return {
            "execution_id": str(execution.id),
            "thread_id": thread_id,
            "status": execution.status,
        }

    async def handle_hitl_response(
        self,
        review_id: str,
        decision: str,
        feedback: str | None = None,
        edits: dict | None = None,
        decided_by: str | None = None,
    ) -> dict:
        """Handle a HITL review response and resume the agent."""
        from app.models.hitl import HITLReview

        # Get the review
        stmt = select(HITLReview).where(HITLReview.id == uuid.UUID(review_id))
        result = await self.db.execute(stmt)
        review = result.scalar_one_or_none()
        if not review:
            raise NotFoundError("HITLReview", review_id)

        # Get the execution
        stmt = select(AgentExecution).where(AgentExecution.id == review.execution_id)
        result = await self.db.execute(stmt)
        execution = result.scalar_one_or_none()
        if not execution:
            raise NotFoundError("AgentExecution", str(review.execution_id))

        # Get phase for project_id
        stmt = select(ProjectPhase).where(ProjectPhase.id == execution.phase_id)
        result = await self.db.execute(stmt)
        phase = result.scalar_one_or_none()

        # Resolve the HITL interrupt
        resume_data = await self.hitl_controller.resolve_interrupt(
            review_id=review_id,
            decision=decision,
            feedback=feedback,
            edits=edits,
            decided_by=decided_by,
            project_id=str(phase.project_id) if phase else None,
        )

        # Resume the agent
        agent_class = get_agent_class(phase.phase_type)
        agent = agent_class(
            llm_provider=self.llm_provider,
            rag_pipeline=self.rag_pipeline,
            event_bus=self.event_bus,
        )
        await agent.compile()

        execution.status = "running"
        await self.db.flush()

        result = await agent.resume(
            thread_id=execution.thread_id,
            human_input=resume_data,
        )

        # Handle post-resume completion
        await self._handle_agent_completion(execution, phase, result)

        return {
            "execution_id": str(execution.id),
            "decision": decision,
            "agent_status": execution.status,
        }

    async def _handle_agent_completion(
        self,
        execution: AgentExecution,
        phase: ProjectPhase,
        result: dict,
    ) -> None:
        """Handle agent execution completion - persist deliverables and transition."""
        phase_status = result.get("phase_status", "completed")

        if phase_status == "completed":
            execution.status = "completed"
            execution.completed_at = datetime.now(timezone.utc)
            phase.status = "completed"
            phase.completed_at = datetime.now(timezone.utc)

            # Persist deliverables
            await self._persist_deliverables(phase, result)

            # Publish completion event
            await self.event_bus.publish_event(Event(
                event_type=EventTypes.PHASE_COMPLETED,
                project_id=str(phase.project_id),
                execution_id=str(execution.id),
                agent_name=execution.agent_name,
                data={"phase_type": phase.phase_type},
            ))

            # Check for next phase
            next_phase_type = PhaseController.get_next_phase(phase.phase_type)
            if next_phase_type and PhaseController.is_phase_ready(next_phase_type):
                # Auto-transition to next phase
                next_phase = await self._get_phase_by_type(str(phase.project_id), next_phase_type)
                if next_phase:
                    await self.start_phase(str(phase.project_id), str(next_phase.id))
            elif not next_phase_type:
                # All phases complete
                project = await self._get_project(str(phase.project_id))
                project.status = "completed"

                await self.event_bus.publish_event(Event(
                    event_type=EventTypes.PROJECT_COMPLETED,
                    project_id=str(phase.project_id),
                ))

        await self.db.flush()

    async def _persist_deliverables(self, phase: ProjectPhase, result: dict) -> None:
        """Persist deliverables from agent output to the database."""
        # Requirements Specification
        if result.get("requirements_spec"):
            spec = result["requirements_spec"]
            await self.deliverable_service.create_deliverable(
                phase_id=phase.id,
                title=spec.get("title", "Requirements Specification"),
                deliverable_type="requirements_spec",
                content=spec.get("content", ""),
                content_structured=spec,
                format="markdown",
                created_by=f"agent:{phase.agent_name}",
            )

        # Traceability Matrix
        if result.get("traceability_matrix"):
            matrix = result["traceability_matrix"]
            import json
            await self.deliverable_service.create_deliverable(
                phase_id=phase.id,
                title=matrix.get("title", "Requirements Traceability Matrix"),
                deliverable_type="traceability_matrix",
                content=json.dumps(matrix, ensure_ascii=False, indent=2),
                content_structured=matrix,
                format="json",
                created_by=f"agent:{phase.agent_name}",
            )

    async def _prepare_phase_input(
        self, project_id: str, phase: ProjectPhase, execution_id: str
    ) -> dict:
        """Prepare the input data for an agent based on the phase type."""
        from app.models.document import Document

        base_input = {
            "project_id": project_id,
            "phase_id": str(phase.id),
            "execution_id": execution_id,
            "messages": [],
            "retrieved_context": [],
            "hitl_status": None,
            "hitl_feedback": None,
            "current_node": None,
            "phase_status": "running",
            "error": None,
        }

        if phase.phase_type == "analysis":
            # Find the development request document
            stmt = (
                select(Document)
                .where(
                    Document.project_id == uuid.UUID(project_id),
                    Document.doc_type == "dev_request",
                )
                .order_by(Document.created_at.desc())
                .limit(1)
            )
            result = await self.db.execute(stmt)
            doc = result.scalar_one_or_none()

            base_input.update({
                "dev_request_doc_id": str(doc.id) if doc else "",
                "document_content": "",
                "raw_requirements": [],
                "functional_requirements": [],
                "non_functional_requirements": [],
                "ambiguities": [],
                "traceability_entries": [],
                "requirements_spec": None,
                "traceability_matrix": None,
            })

        return base_input

    async def _get_project(self, project_id: str) -> Project:
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Project)
            .options(selectinload(Project.phases))
            .where(Project.id == uuid.UUID(project_id))
        )
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError("Project", project_id)
        return project

    async def _get_phase(self, phase_id: str) -> ProjectPhase:
        stmt = select(ProjectPhase).where(ProjectPhase.id == uuid.UUID(phase_id))
        result = await self.db.execute(stmt)
        phase = result.scalar_one_or_none()
        if not phase:
            raise NotFoundError("ProjectPhase", phase_id)
        return phase

    async def _get_phase_by_type(self, project_id: str, phase_type: str) -> ProjectPhase | None:
        stmt = select(ProjectPhase).where(
            ProjectPhase.project_id == uuid.UUID(project_id),
            ProjectPhase.phase_type == phase_type,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
