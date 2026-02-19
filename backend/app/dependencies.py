"""Shared dependency injection providers."""

from __future__ import annotations
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db

if TYPE_CHECKING:
    from app.llm.provider import LLMProvider
    from app.orchestration.event_bus import EventBus
    from app.rag.pipeline import RAGPipeline

security_scheme = HTTPBearer(auto_error=False)

# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> str | None:
    """Extract current user ID from JWT token. Returns None if no token."""
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload.get("sub")


CurrentUserID = Annotated[str | None, Depends(get_current_user_id)]


# ---------------------------------------------------------------------------
# Service singletons (created in app lifespan, stored on app.state)
# ---------------------------------------------------------------------------


def get_llm_provider(request: Request) -> Any:
    """Get the application-scoped LLM provider."""
    return request.app.state.llm_provider


def get_rag_pipeline(request: Request) -> Any:
    """Get the application-scoped RAG pipeline."""
    return request.app.state.rag_pipeline


def get_event_bus(request: Request) -> Any:
    """Get the application-scoped event bus."""
    return request.app.state.event_bus


LLMProviderDep = Annotated[Any, Depends(get_llm_provider)]
RAGPipelineDep = Annotated[Any, Depends(get_rag_pipeline)]
EventBusDep = Annotated[Any, Depends(get_event_bus)]
