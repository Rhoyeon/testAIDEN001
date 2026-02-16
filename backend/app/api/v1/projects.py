"""Project management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import CurrentUserID, DBSession
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("", response_model=SuccessResponse[ProjectDetailResponse])
async def create_project(data: ProjectCreate, db: DBSession, user_id: CurrentUserID):
    """Create a new project with default phases."""
    service = ProjectService(db)
    project = await service.create_project(data, owner_id=user_id)
    return SuccessResponse(data=ProjectDetailResponse.model_validate(project))


@router.get("", response_model=PaginatedResponse[ProjectListResponse])
async def list_projects(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all projects with pagination."""
    service = ProjectService(db)
    offset = (page - 1) * page_size
    projects, total = await service.list_projects(offset=offset, limit=page_size)
    return PaginatedResponse(
        data=[ProjectListResponse.model_validate(p) for p in projects],
        meta={"page": page, "page_size": page_size, "total": total},
    )


@router.get("/{project_id}", response_model=SuccessResponse[ProjectDetailResponse])
async def get_project(project_id: UUID, db: DBSession):
    """Get project details with phases."""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    return SuccessResponse(data=ProjectDetailResponse.model_validate(project))


@router.patch("/{project_id}", response_model=SuccessResponse[ProjectDetailResponse])
async def update_project(project_id: UUID, data: ProjectUpdate, db: DBSession):
    """Update project details."""
    service = ProjectService(db)
    project = await service.update_project(project_id, data)
    return SuccessResponse(data=ProjectDetailResponse.model_validate(project))


@router.delete("/{project_id}", response_model=SuccessResponse[dict])
async def delete_project(project_id: UUID, db: DBSession):
    """Archive a project (soft delete)."""
    service = ProjectService(db)
    await service.delete_project(project_id)
    return SuccessResponse(data={"message": "Project archived successfully"})


@router.post("/{project_id}/start", response_model=SuccessResponse[ProjectDetailResponse])
async def start_project(project_id: UUID, db: DBSession):
    """Start the project workflow (begins analysis phase)."""
    service = ProjectService(db)
    project = await service.start_project(project_id)
    return SuccessResponse(data=ProjectDetailResponse.model_validate(project))
