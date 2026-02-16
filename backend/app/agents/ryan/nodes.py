"""Node functions for Ryan analysis agent."""

import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt

from app.agents.base.nodes import format_context, rag_retrieve_node
from app.agents.ryan.prompts import (
    BUILD_TRACEABILITY_PROMPT,
    CLASSIFY_REQUIREMENTS_PROMPT,
    DETECT_AMBIGUITIES_PROMPT,
    EXTRACT_REQUIREMENTS_PROMPT,
    GENERATE_SPEC_PROMPT,
    SYSTEM_PROMPT,
)
from app.agents.ryan.schemas import (
    AmbiguityListOutput,
    RequirementsListOutput,
    TraceabilityMatrixOutput,
)
from app.agents.ryan.state import RyanState
from app.llm.provider import LLMProvider
from app.rag.pipeline import RAGPipeline


def create_ryan_nodes(llm_provider: LLMProvider, rag_pipeline: RAGPipeline):
    """Factory that creates all Ryan agent node functions with injected dependencies."""

    async def load_document(state: RyanState) -> dict:
        """Load the development request document content."""
        doc_id = state["dev_request_doc_id"]
        project_id = state["project_id"]

        # Retrieve all chunks for this document from the RAG store
        results = await rag_pipeline.retrieve(
            query="전체 문서 내용 요약",  # "Summarize entire document content"
            project_id=project_id,
            top_k=50,
            filters={"document_id": doc_id} if doc_id else None,
        )

        # Combine all chunks to reconstruct document
        if results:
            content = "\n\n".join([r["content"] for r in results])
        else:
            content = "[Document content not found in vector store]"

        return {
            "document_content": content,
            "current_node": "load_document",
            "phase_status": "running",
        }

    async def retrieve_context(state: RyanState) -> dict:
        """Retrieve relevant context from RAG for requirements analysis."""
        project_id = state["project_id"]
        doc_content = state.get("document_content", "")

        # Generate multiple queries for comprehensive retrieval
        queries = [
            "기능 요구사항 functional requirements",
            "비기능 요구사항 non-functional requirements performance security",
            "시스템 제약사항 constraints limitations",
            "사용자 스토리 user stories use cases",
            "인터페이스 요구사항 interface requirements API",
        ]

        results = await rag_pipeline.retrieve_multi_query(
            queries=queries,
            project_id=project_id,
            top_k_per_query=5,
        )

        return {
            "retrieved_context": results,
            "current_node": "retrieve_context",
        }

    async def extract_requirements(state: RyanState) -> dict:
        """Extract requirements from the document using LLM."""
        llm = llm_provider.get_model_for_task("requirement_extraction")
        structured_llm = llm.with_structured_output(RequirementsListOutput)

        context = format_context(state.get("retrieved_context", []))
        prompt = EXTRACT_REQUIREMENTS_PROMPT.format(
            document_content=state.get("document_content", ""),
            context=context,
        )

        result = await structured_llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        requirements = [req.model_dump() for req in result.requirements]

        return {
            "raw_requirements": requirements,
            "current_node": "extract_requirements",
        }

    async def classify_requirements(state: RyanState) -> dict:
        """Classify requirements into functional and non-functional."""
        llm = llm_provider.get_model_for_task("requirement_classification")

        requirements = state.get("raw_requirements", [])

        # Separate by category
        functional = [r for r in requirements if r.get("category") == "functional"]
        non_functional = [r for r in requirements if r.get("category") == "non_functional"]

        return {
            "functional_requirements": functional,
            "non_functional_requirements": non_functional,
            "current_node": "classify_requirements",
        }

    async def detect_ambiguities(state: RyanState) -> dict:
        """Detect ambiguities and unclear points in requirements."""
        llm = llm_provider.get_model_for_task("ambiguity_detection")
        structured_llm = llm.with_structured_output(AmbiguityListOutput)

        all_requirements = (
            state.get("functional_requirements", [])
            + state.get("non_functional_requirements", [])
        )
        context = format_context(state.get("retrieved_context", []))

        prompt = DETECT_AMBIGUITIES_PROMPT.format(
            requirements=json.dumps(all_requirements, ensure_ascii=False, indent=2),
            context=context,
        )

        result = await structured_llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        ambiguities = [a.model_dump() for a in result.ambiguities]

        return {
            "ambiguities": ambiguities,
            "current_node": "detect_ambiguities",
        }

    async def hitl_ambiguity_review(state: RyanState) -> dict:
        """HITL interrupt point for ambiguity review."""
        ambiguities = state.get("ambiguities", [])

        if not ambiguities:
            return {
                "hitl_status": "approved",
                "current_node": "hitl_ambiguity_review",
            }

        # Trigger HITL interrupt - execution pauses here
        review_result = interrupt({
            "review_type": "ambiguity_review",
            "message": f"{len(ambiguities)} ambiguities detected in requirements. Please review.",
            "ambiguities": ambiguities,
            "requirements": (
                state.get("functional_requirements", [])
                + state.get("non_functional_requirements", [])
            ),
        })

        # When resumed, review_result contains the human's decision
        return {
            "hitl_status": review_result.get("decision", "approved"),
            "hitl_feedback": review_result,
            "current_node": "hitl_ambiguity_review",
        }

    async def refine_requirements(state: RyanState) -> dict:
        """Refine requirements based on HITL feedback."""
        feedback = state.get("hitl_feedback")
        functional = state.get("functional_requirements", [])
        non_functional = state.get("non_functional_requirements", [])

        if feedback and feedback.get("edits"):
            edits = feedback["edits"]

            # Apply edits to requirements
            all_reqs = {r["id"]: r for r in functional + non_functional}

            for req_id, changes in edits.items():
                if req_id in all_reqs:
                    all_reqs[req_id].update(changes)

            # Re-separate after edits
            functional = [r for r in all_reqs.values() if r.get("category") == "functional"]
            non_functional = [r for r in all_reqs.values() if r.get("category") == "non_functional"]

        return {
            "functional_requirements": functional,
            "non_functional_requirements": non_functional,
            "current_node": "refine_requirements",
        }

    async def build_traceability(state: RyanState) -> dict:
        """Build the requirements traceability matrix."""
        llm = llm_provider.get_model_for_task("traceability_mapping")
        structured_llm = llm.with_structured_output(TraceabilityMatrixOutput)

        all_requirements = (
            state.get("functional_requirements", [])
            + state.get("non_functional_requirements", [])
        )

        prompt = BUILD_TRACEABILITY_PROMPT.format(
            requirements=json.dumps(all_requirements, ensure_ascii=False, indent=2),
            document_content=state.get("document_content", "")[:5000],
        )

        result = await structured_llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        entries = [e.model_dump() for e in result.entries]

        return {
            "traceability_entries": entries,
            "current_node": "build_traceability",
        }

    async def generate_spec_document(state: RyanState) -> dict:
        """Generate the requirements specification document."""
        llm = llm_provider.get_model_for_task("document_generation")

        all_requirements = (
            state.get("functional_requirements", [])
            + state.get("non_functional_requirements", [])
        )
        traceability = state.get("traceability_entries", [])
        context = format_context(state.get("retrieved_context", []))

        prompt = GENERATE_SPEC_PROMPT.format(
            requirements=json.dumps(all_requirements, ensure_ascii=False, indent=2),
            traceability=json.dumps(traceability, ensure_ascii=False, indent=2),
            context=context[:3000],
        )

        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        requirements_spec = {
            "title": "Requirements Specification",
            "content": response.content,
            "functional_count": len(state.get("functional_requirements", [])),
            "non_functional_count": len(state.get("non_functional_requirements", [])),
            "requirements": all_requirements,
        }

        traceability_matrix = {
            "title": "Requirements Traceability Matrix",
            "entries": traceability,
            "total_requirements": len(all_requirements),
        }

        return {
            "requirements_spec": requirements_spec,
            "traceability_matrix": traceability_matrix,
            "current_node": "generate_spec_document",
        }

    async def hitl_final_review(state: RyanState) -> dict:
        """HITL interrupt point for final deliverable review."""
        review_result = interrupt({
            "review_type": "final_deliverable_review",
            "message": "Requirements specification and traceability matrix are ready for review.",
            "requirements_spec": state.get("requirements_spec"),
            "traceability_matrix": state.get("traceability_matrix"),
        })

        return {
            "hitl_status": review_result.get("decision", "approved"),
            "hitl_feedback": review_result,
            "current_node": "hitl_final_review",
        }

    async def finalize_deliverables(state: RyanState) -> dict:
        """Finalize deliverables after approval."""
        return {
            "phase_status": "completed",
            "current_node": "finalize_deliverables",
        }

    return {
        "load_document": load_document,
        "retrieve_context": retrieve_context,
        "extract_requirements": extract_requirements,
        "classify_requirements": classify_requirements,
        "detect_ambiguities": detect_ambiguities,
        "hitl_ambiguity_review": hitl_ambiguity_review,
        "refine_requirements": refine_requirements,
        "build_traceability": build_traceability,
        "generate_spec_document": generate_spec_document,
        "hitl_final_review": hitl_final_review,
        "finalize_deliverables": finalize_deliverables,
    }
