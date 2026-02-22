"""Document management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.config import settings
from app.core.logging import get_logger
from app.dependencies import CurrentUserID, DBSession
from app.schemas.common import SuccessResponse
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter()
logger = get_logger("api.documents")


@router.post("/projects/{project_id}/upload", response_model=SuccessResponse[DocumentUploadResponse])
async def upload_document(
    project_id: UUID,
    request: Request,
    db: DBSession,
    user_id: CurrentUserID,
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form(default="dev_request"),
):
    """Upload a document to a project and ingest into RAG pipeline."""
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.max_upload_size_mb}MB",
        )

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

    # RAG ingestion - index document for agent retrieval (non-blocking)
    try:
        rag = request.app.state.rag_pipeline
        ingest_result = await rag.ingest_document(
            document_id=str(document.id),
            project_id=str(project_id),
            file_path=document.file_path,
            mime_type=document.mime_type,
            doc_type=document.doc_type,
        )
        await service.mark_indexed(document.id, ingest_result.get("content_text"))
        logger.info(
            f"Document indexed: {document.id} "
            f"({ingest_result.get('chunk_count', 0)} chunks)"
        )
    except Exception as e:
        logger.warning(f"RAG ingestion failed for document {document.id}: {e}")

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
