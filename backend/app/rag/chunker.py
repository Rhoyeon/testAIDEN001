"""Text chunking strategies for RAG pipeline."""

from dataclasses import dataclass, field
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    """A text chunk with metadata."""
    content: str
    index: int
    metadata: dict = field(default_factory=dict)


# Korean-aware separators
KOREAN_SEPARATORS = ["\n\n", "\n", ". ", ".\n", "。", " ", ""]

# Chunking strategies per document type
CHUNK_STRATEGIES: Dict[str, dict] = {
    "dev_request": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "separators": KOREAN_SEPARATORS,
    },
    "requirements_spec": {
        "chunk_size": 1500,
        "chunk_overlap": 300,
        "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    },
    "design_doc": {
        "chunk_size": 1200,
        "chunk_overlap": 250,
        "separators": ["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    },
    "default": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "separators": KOREAN_SEPARATORS,
    },
}


class TextChunker:
    """Splits text into chunks using configurable strategies."""

    def __init__(self, default_chunk_size: int = 1000, default_chunk_overlap: int = 200):
        self.default_chunk_size = default_chunk_size
        self.default_chunk_overlap = default_chunk_overlap

    def split(
        self,
        text: str,
        doc_type: str = "default",
        metadata: dict | None = None,
    ) -> List[Chunk]:
        """Split text into chunks based on document type strategy."""
        strategy = CHUNK_STRATEGIES.get(doc_type, CHUNK_STRATEGIES["default"])

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=strategy["chunk_size"],
            chunk_overlap=strategy["chunk_overlap"],
            separators=strategy["separators"],
            length_function=len,
            is_separator_regex=False,
        )

        documents = splitter.create_documents(
            texts=[text],
            metadatas=[metadata or {}],
        )

        chunks = []
        for i, doc in enumerate(documents):
            chunk_meta = {**(metadata or {}), "chunk_index": i}
            chunks.append(Chunk(content=doc.page_content, index=i, metadata=chunk_meta))

        return chunks
