"""Document management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.config import settings
from app.dependencies import CurrentUserID, DBSession
from app.schemas.common import SuccessResponse
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/projects/{project_id}/upload", response_model=SuccessResponse[DocumentUploadResponse])
async def upload_document(
    project_id: UUID,
    db: DBSession,
    user_id: CurrentUserID,
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form(default="dev_request"),
):
    """Upload a document to a project."""
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise ValueError(f"File size exceeds maximum of {settings.max_upload_size_mb}MB")

    service = DocumentService(db)
    document = await service.upload_document(
        project_id=project_id,
        title=title,
        doc_type=doc_type,
        file_name=file.filename or "unnamed",
        file_content=content,
        mime_type=file.content_type or "application/octet-stream",
        uploaded_by=user_id,
    )
    return SuccessResponse(data=DocumentUploadResponse.model_validate(document))


@router.get("/projects/{project_id}", response_model=SuccessResponse[list[DocumentResponse]])
async def list_project_documents(project_id: UUID, db: DBSession):
    """List all documents for a project."""
    service = DocumentService(db)
    documents = await service.list_documents(project_id)
    return SuccessResponse(data=[DocumentResponse.model_validate(d) for d in documents])


@router.get("/{document_id}", response_model=SuccessResponse[DocumentResponse])
async def get_document(document_id: UUID, db: DBSession):
    """Get document details."""
    service = DocumentService(db)
    document = await service.get_document(document_id)
    return SuccessResponse(data=DocumentResponse.model_validate(document))
