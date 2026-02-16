"""Ryan agent state definition - Analysis phase."""

from __future__ import annotations
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class Requirement(TypedDict):
    """A single requirement extracted from the development request."""
    id: str
    title: str
    description: str
    category: str            # 'functional' | 'non_functional'
    priority: str            # 'high' | 'medium' | 'low'
    source_reference: str    # Reference to source in dev request
    acceptance_criteria: list[str]


class Ambiguity(TypedDict):
    """An ambiguity or unclear point detected in requirements."""
    requirement_id: str
    description: str
    suggestion: str
    severity: str            # 'high' | 'medium' | 'low'


class TraceabilityEntry(TypedDict):
    """Maps a requirement to its source in the development request."""
    requirement_id: str
    requirement_title: str
    source_section: str
    source_text: str
    verification_method: str


class RyanState(TypedDict):
    """State for the Ryan analysis agent."""

    # Input
    project_id: str
    phase_id: str
    execution_id: str
    dev_request_doc_id: str

    # LLM messages
    messages: Annotated[list, add_messages]

    # Working data
    document_content: str
    retrieved_context: list[dict]
    raw_requirements: list[dict]
    functional_requirements: list[dict]
    non_functional_requirements: list[dict]
    ambiguities: list[dict]

    # Traceability
    traceability_entries: list[dict]

    # HITL state
    hitl_status: str | None
    hitl_feedback: dict | None

    # Output deliverables
    requirements_spec: dict | None
    traceability_matrix: dict | None

    # Execution tracking
    current_node: str | None
    phase_status: str
    error: str | None
