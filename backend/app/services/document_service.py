"""Document management service."""

import os
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import NotFoundError
from app.models.document import Document


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_document(
        self,
        project_id: uuid.UUID,
        title: str,
        doc_type: str,
        file_name: str,
        file_content: bytes,
        mime_type: str,
        uploaded_by: str | None = None,
    ) -> Document:
        """Upload and store a document."""
        # Ensure upload directory exists
        upload_dir = Path(settings.upload_dir) / str(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_dir / file_name
        file_path.write_bytes(file_content)

        document = Document(
            project_id=project_id,
            title=title,
            doc_type=doc_type,
            file_path=str(file_path),
            file_name=file_name,
            file_size=len(file_content),
            mime_type=mime_type,
            is_indexed=False,
            uploaded_by=uuid.UUID(uploaded_by) if uploaded_by else None,
        )
        self.db.add(document)
        await self.db.flush()
        return document

    async def get_document(self, document_id: uuid.UUID) -> Document:
        """Get a document by ID."""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            raise NotFoundError("Document", str(document_id))
        return document

    async def list_documents(self, project_id: uuid.UUID) -> list[Document]:
        """List all documents for a project."""
        stmt = (
            select(Document)
            .where(Document.project_id == project_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_indexed(self, document_id: uuid.UUID, content_text: str | None = None) -> Document:
        """Mark a document as indexed after RAG processing."""
        document = await self.get_document(document_id)
        document.is_indexed = True
        if content_text:
            document.content_text = content_text
        await self.db.flush()
        return document
