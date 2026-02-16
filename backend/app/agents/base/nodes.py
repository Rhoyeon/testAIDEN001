"""Reusable node functions shared across agents."""

from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from app.rag.pipeline import RAGPipeline


async def rag_retrieve_node(
    query: str,
    project_id: str,
    rag_pipeline: RAGPipeline,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """Reusable RAG retrieval function for agent nodes."""
    results = await rag_pipeline.retrieve(
        query=query,
        project_id=project_id,
        top_k=top_k,
    )
    return results


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into a context string for LLM prompts."""
    if not chunks:
        return "No relevant context found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("doc_type", "unknown")
        score = chunk.get("relevance_score", 0)
        content = chunk["content"]
        context_parts.append(
            f"[Context {i} | Source: {source} | Relevance: {score:.2f}]\n{content}"
        )

    return "\n\n---\n\n".join(context_parts)


async def llm_call(
    llm: BaseChatModel,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Make a single LLM call with system + user messages."""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = await llm.ainvoke(messages)
    return response.content


async def llm_structured_call(
    llm: BaseChatModel,
    system_prompt: str,
    user_prompt: str,
    output_schema: type,
) -> Any:
    """Make an LLM call with structured output parsing."""
    structured_llm = llm.with_structured_output(output_schema)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    return await structured_llm.ainvoke(messages)
