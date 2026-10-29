from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool
    data: Optional[T] = None
    message: Optional[str] = None


class APIError(BaseModel):
    """Standard API error response."""

    success: bool = False
    error_code: str
    message: str
