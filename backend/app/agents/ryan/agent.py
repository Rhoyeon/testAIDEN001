"""Ryan Agent - Analysis phase agent for AIDEN platform.

Ryan analyzes development request documents and produces:
1. Requirements Specification (요구사항명세서)
2. Requirements Traceability Matrix (요구사항 추적매트릭스)

Workflow:
  START -> load_document -> retrieve_context -> extract_requirements
       -> classify_requirements -> detect_ambiguities
       -> [if ambiguities] hitl_ambiguity_review -> refine_requirements
       -> [if no ambiguities] refine_requirements
       -> build_traceability -> generate_spec_document
       -> hitl_final_review
       -> [if approved] finalize_deliverables -> END
       -> [if revision] refine_requirements (loop back)
"""

from typing import Type

from langgraph.graph import END, START, StateGraph

from app.agents import register_agent
from app.agents.base.agent import BaseAgent
from app.agents.ryan.nodes import create_ryan_nodes
from app.agents.ryan.state import RyanState


@register_agent("analysis")
class RyanAgent(BaseAgent):
    """Analysis phase agent - extracts and structures requirements."""

    def __init__(self, **kwargs):
        super().__init__(agent_name="ryan", **kwargs)
        self._nodes = create_ryan_nodes(self.llm_provider, self.rag_pipeline)

    def get_state_class(self) -> Type:
        return RyanState

    def build_graph(self, builder: StateGraph) -> StateGraph:
        """Build the Ryan agent LangGraph."""

        # Add all nodes
        for name, func in self._nodes.items():
            builder.add_node(name, func)

        # Define the flow
        builder.add_edge(START, "load_document")
        builder.add_edge("load_document", "retrieve_context")
        builder.add_edge("retrieve_context", "extract_requirements")
        builder.add_edge("extract_requirements", "classify_requirements")
        builder.add_edge("classify_requirements", "detect_ambiguities")

        # Conditional: ambiguities found -> HITL review, else skip
        builder.add_conditional_edges(
            "detect_ambiguities",
            self._route_ambiguity_check,
            {
                "needs_review": "hitl_ambiguity_review",
                "no_issues": "refine_requirements",
            },
        )

        builder.add_edge("hitl_ambiguity_review", "refine_requirements")
        builder.add_edge("refine_requirements", "build_traceability")
        builder.add_edge("build_traceability", "generate_spec_document")
        builder.add_edge("generate_spec_document", "hitl_final_review")

        # Conditional: final review -> approved or revision loop
        builder.add_conditional_edges(
            "hitl_final_review",
            self._route_final_review,
            {
                "approved": "finalize_deliverables",
                "revision": "refine_requirements",
            },
        )

        builder.add_edge("finalize_deliverables", END)

        return builder

    @staticmethod
    def _route_ambiguity_check(state: RyanState) -> str:
        """Route based on whether ambiguities were detected."""
        ambiguities = state.get("ambiguities", [])
        if ambiguities and len(ambiguities) > 0:
            return "needs_review"
        return "no_issues"

    @staticmethod
    def _route_final_review(state: RyanState) -> str:
        """Route based on final HITL review decision."""
        hitl_status = state.get("hitl_status", "approved")
        if hitl_status == "approved":
            return "approved"
        return "revision"
