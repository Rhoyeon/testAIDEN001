"""Embedding generation for RAG pipeline."""

from __future__ import annotations
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.core.logging import get_logger

logger = get_logger("rag.embedder")


class Embedder:
    """Generates embeddings using configured embedding model."""

    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._embeddings = OpenAIEmbeddings(
            model=self.model_name,
            api_key=api_key or settings.openai_api_key,
        )

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Get the LangChain embeddings instance."""
        return self._embeddings

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        logger.debug(f"Embedding {len(texts)} texts with {self.model_name}")
        return await self._embeddings.aembed_documents(texts)

    async def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        return await self._embeddings.aembed_query(query)
