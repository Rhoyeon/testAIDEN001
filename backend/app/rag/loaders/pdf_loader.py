"""PDF document loader."""

import asyncio

from pypdf import PdfReader

from app.rag.loaders.base import BaseDocumentLoader, LoadedDocument


class PDFLoader(BaseDocumentLoader):
    """Loads PDF documents and extracts text content."""

    SUPPORTED_TYPES = {"application/pdf"}

    def supports_mime_type(self, mime_type: str) -> bool:
        return mime_type in self.SUPPORTED_TYPES

    async def load(self, file_path: str) -> LoadedDocument:
        """Extract text from PDF using pypdf."""
        def _extract():
            reader = PdfReader(file_path)
            pages = []
            metadata = {"page_count": len(reader.pages)}

            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"[Page {i + 1}]\n{text}")

            return LoadedDocument(
                text="\n\n".join(pages),
                metadata=metadata,
            )

        return await asyncio.to_thread(_extract)
