"""Base document loader interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LoadedDocument:
    """Result of document loading."""
    text: str
    metadata: dict


class BaseDocumentLoader(ABC):
    """Abstract base for all document loaders."""

    @abstractmethod
    async def load(self, file_path: str) -> LoadedDocument:
        """Load a document and extract its text content."""
        ...

    @abstractmethod
    def supports_mime_type(self, mime_type: str) -> bool:
        """Check if this loader supports the given MIME type."""
        ...
