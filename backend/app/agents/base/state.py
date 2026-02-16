"""Base state definitions and utilities shared across all agents."""

from typing import Annotated, Any, TypedDict

from langgraph.graph import add_messages


class BaseAgentState(TypedDict):
    """Common state fields shared by all AIDEN agents."""

    # Project context
    project_id: str
    phase_id: str
    execution_id: str

    # Messages for LLM conversation
    messages: Annotated[list, add_messages]

    # RAG context
    retrieved_context: list[dict]

    # HITL state
    hitl_status: str | None      # 'pending', 'approved', 'rejected', 'revision_requested'
    hitl_feedback: dict | None

    # Execution tracking
    current_node: str | None
    phase_status: str             # 'running', 'hitl_review', 'completed', 'failed'
    error: str | None


def merge_lists(left: list, right: list) -> list:
    """Reducer that merges two lists (appends right to left)."""
    return left + right
