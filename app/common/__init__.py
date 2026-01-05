"""
Common utilities and shared code across the application.
"""
from .enums import CourseStatus, UserRole
from .exceptions import (
    ConflictError,
    DomainException,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from .schemas import AuthResponse, UserResponse
from .types import ModelType
from .utils.pagination import PaginatedResponse, PaginationMeta, PaginationParams

__all__ = [
    "UserRole",
    "CourseStatus",
    "ModelType",
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "AuthResponse",
    "UserResponse",
    "DomainException",
    "ValidationError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "InternalServerError",
]
