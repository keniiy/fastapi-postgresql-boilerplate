"""
Common utilities and shared code across the application.
"""
from .enums import UserRole, CourseStatus
from .types import ModelType
from .utils.pagination import PaginationParams, PaginationMeta, PaginatedResponse
from .schemas import AuthResponse, UserResponse
from .exceptions import (
    DomainException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError,
)

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
