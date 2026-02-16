"""RAG pipeline orchestrator - manages document ingestion and retrieval."""

from typing import Any, Dict, List

from app.core.exceptions import DocumentProcessingError, RAGPipelineError
from app.core.logging import get_logger
from app.rag.chunker import TextChunker
from app.rag.embedder import Embedder
from app.rag.loaders.base import BaseDocumentLoader
from app.rag.loaders.docx_loader import DocxLoader
from app.rag.loaders.pdf_loader import PDFLoader
from app.rag.retriever import Retriever
from app.rag.vectorstore import ChromaVectorStore

logger = get_logger("rag.pipeline")


class RAGPipeline:
    """Orchestrates document ingestion and retrieval for AIDEN agents."""

    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or Embedder()
        self.vectorstore = ChromaVectorStore(self.embedder)
        self.chunker = TextChunker()
        self.retriever = Retriever(self.vectorstore)

        # Register document loaders
        self._loaders: List[BaseDocumentLoader] = [
            PDFLoader(),
            DocxLoader(),
        ]

    def _get_loader(self, mime_type: str) -> BaseDocumentLoader:
        """Find a loader that supports the given MIME type."""
        for loader in self._loaders:
            if loader.supports_mime_type(mime_type):
                return loader
        raise DocumentProcessingError(
            document_id="unknown",
            message=f"No loader available for MIME type: {mime_type}",
        )

    async def ingest_document(
        self,
        document_id: str,
        project_id: str,
        file_path: str,
        mime_type: str,
        doc_type: str = "default",
        extra_metadata: dict | None = None,
    ) -> dict:
        """Full document ingestion pipeline: load -> chunk -> embed -> store.

        Returns summary with chunk count and document text.
        """
        logger.info(f"Starting ingestion for document {document_id} ({mime_type})")

        try:
            # 1. Load document
            loader = self._get_loader(mime_type)
            loaded = await loader.load(file_path)
            logger.info(f"Loaded document: {len(loaded.text)} chars")

            # 2. Chunk the text
            metadata = {
                "document_id": document_id,
                "project_id": project_id,
                "doc_type": doc_type,
                **(extra_metadata or {}),
                **loaded.metadata,
            }
            chunks = self.chunker.split(
                text=loaded.text,
                doc_type=doc_type,
                metadata=metadata,
            )
            logger.info(f"Created {len(chunks)} chunks")

            # 3. Store in vector DB
            chunk_ids = await self.vectorstore.add_chunks(
                chunks=chunks,
                project_id=project_id,
            )
            logger.info(f"Stored {len(chunk_ids)} vectors in ChromaDB")

            return {
                "document_id": document_id,
                "chunk_count": len(chunks),
                "text_length": len(loaded.text),
                "content_text": loaded.text,
                "document_metadata": loaded.metadata,
            }

        except DocumentProcessingError:
            raise
        except Exception as e:
            raise RAGPipelineError(
                stage="ingest",
                message=f"Failed to ingest document {document_id}: {str(e)}",
            )

    async def retrieve(
        self,
        query: str,
        project_id: str,
        top_k: int = 10,
        min_relevance: float = 0.3,
        filters: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a query."""
        return await self.retriever.retrieve(
            query=query,
            project_id=project_id,
            top_k=top_k,
            min_relevance=min_relevance,
            filters=filters,
        )

    async def retrieve_multi_query(
        self,
        queries: List[str],
        project_id: str,
        top_k_per_query: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve using multiple queries for comprehensive coverage."""
        return await self.retriever.retrieve_multi_query(
            queries=queries,
            project_id=project_id,
            top_k_per_query=top_k_per_query,
        )
