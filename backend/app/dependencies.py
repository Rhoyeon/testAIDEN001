"""Shared dependency injection providers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db

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
