"""Retrieval strategies for RAG pipeline."""

from typing import Any, Dict, List

from app.core.logging import get_logger
from app.rag.vectorstore import ChromaVectorStore

logger = get_logger("rag.retriever")


class Retriever:
    """Retrieves relevant document chunks with configurable strategies."""

    def __init__(self, vectorstore: ChromaVectorStore):
        self.vectorstore = vectorstore

    async def retrieve(
        self,
        query: str,
        project_id: str,
        top_k: int = 10,
        min_relevance: float = 0.3,
        filters: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks with relevance filtering."""
        results = await self.vectorstore.similarity_search(
            query=query,
            project_id=project_id,
            k=top_k,
            filters=filters,
        )

        # Filter by minimum relevance score
        filtered = [r for r in results if r.get("relevance_score", 0) >= min_relevance]

        logger.info(
            f"Retrieved {len(filtered)}/{len(results)} chunks for query "
            f"(min_relevance={min_relevance})"
        )
        return filtered

    async def retrieve_for_document(
        self,
        query: str,
        project_id: str,
        document_id: str,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve chunks from a specific document."""
        return await self.retrieve(
            query=query,
            project_id=project_id,
            top_k=top_k,
            filters={"document_id": document_id},
        )

    async def retrieve_multi_query(
        self,
        queries: List[str],
        project_id: str,
        top_k_per_query: int = 5,
        deduplicate: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retrieve using multiple queries and merge results."""
        all_results: List[Dict[str, Any]] = []
        seen_contents = set()

        for query in queries:
            results = await self.retrieve(
                query=query,
                project_id=project_id,
                top_k=top_k_per_query,
            )
            for result in results:
                content_key = result["content"][:100]
                if not deduplicate or content_key not in seen_contents:
                    seen_contents.add(content_key)
                    all_results.append(result)

        # Sort by relevance score
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return all_results
