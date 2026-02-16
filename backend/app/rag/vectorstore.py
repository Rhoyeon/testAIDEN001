"""ChromaDB vector store wrapper."""

from typing import Any, Dict, List

import chromadb
from langchain_chroma import Chroma

from app.config import settings
from app.core.logging import get_logger
from app.rag.chunker import Chunk
from app.rag.embedder import Embedder

logger = get_logger("rag.vectorstore")


class ChromaVectorStore:
    """Manages ChromaDB collections for per-project vector storage."""

    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self._client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )

    def _get_collection_name(self, project_id: str) -> str:
        """Generate a collection name for a project."""
        return f"project_{project_id.replace('-', '_')}"

    def _get_langchain_store(self, project_id: str) -> Chroma:
        """Get a LangChain Chroma instance for a project."""
        return Chroma(
            client=self._client,
            collection_name=self._get_collection_name(project_id),
            embedding_function=self.embedder.embeddings,
        )

    async def add_chunks(
        self,
        chunks: List[Chunk],
        project_id: str,
    ) -> List[str]:
        """Add document chunks to the project's vector store."""
        store = self._get_langchain_store(project_id)

        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{project_id}_{chunk.metadata.get('document_id', 'doc')}_{chunk.index}" for chunk in chunks]

        logger.info(f"Adding {len(chunks)} chunks to collection for project {project_id}")

        result_ids = await store.aadd_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )
        return result_ids

    async def similarity_search(
        self,
        query: str,
        project_id: str,
        k: int = 10,
        filters: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks in a project's collection."""
        store = self._get_langchain_store(project_id)

        results = await store.asimilarity_search_with_relevance_scores(
            query=query,
            k=k,
            filter=filters,
        )

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score,
            }
            for doc, score in results
        ]

    async def delete_collection(self, project_id: str) -> None:
        """Delete a project's entire vector collection."""
        collection_name = self._get_collection_name(project_id)
        try:
            self._client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Failed to delete collection {collection_name}: {e}")
