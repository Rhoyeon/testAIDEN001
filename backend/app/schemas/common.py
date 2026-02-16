"""Common response schemas used across all endpoints."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope."""
    success: bool = True
    data: T


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response envelope."""
    success: bool = True
    data: list[T]
    meta: dict[str, int]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    success: bool = False
    error: ErrorDetail


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
