"""Agent execution monitoring API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DBSession
from app.models.agent import AgentExecution, AgentLog
from app.schemas.agent import AgentExecutionResponse, AgentLogResponse
from app.schemas.common import PaginatedResponse, SuccessResponse

router = APIRouter()


@router.get("/{execution_id}", response_model=SuccessResponse[AgentExecutionResponse])
async def get_agent_execution(execution_id: UUID, db: DBSession):
    """Get agent execution details."""
    stmt = select(AgentExecution).where(AgentExecution.id == execution_id)
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()
    if not execution:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("AgentExecution", str(execution_id))
    return SuccessResponse(data=AgentExecutionResponse.model_validate(execution))


@router.get("/{execution_id}/logs", response_model=PaginatedResponse[AgentLogResponse])
async def get_agent_logs(
    execution_id: UUID,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Get agent execution logs with pagination."""
    offset = (page - 1) * page_size

    # Count
    count_stmt = select(AgentLog).where(AgentLog.execution_id == execution_id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    # Fetch
    stmt = (
        select(AgentLog)
        .where(AgentLog.execution_id == execution_id)
        .order_by(AgentLog.created_at)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    logs = list(result.scalars().all())

    return PaginatedResponse(
        data=[AgentLogResponse.model_validate(log) for log in logs],
        meta={"page": page, "page_size": page_size, "total": total},
    )
