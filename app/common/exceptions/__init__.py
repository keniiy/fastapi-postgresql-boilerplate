"""
Comprehensive domain exceptions with error codes.
"""
from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base exception for all domain errors"""

    def __init__(self, message: str, code: str = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or self._get_default_code()
        self.details = details or {}
        super().__init__(self.message)

    def _get_default_code(self) -> str:
        """Get default error code from class name"""
        return self.__class__.__name__.upper().replace("ERROR", "_ERROR")


class ValidationError(DomainException):
    """400 - Validation error"""

    def __init__(self, message: str, field: str = None, **kwargs):
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)


class NotFoundError(DomainException):
    """404 - Resource not found"""

    def __init__(self, message: str, resource: str = None, **kwargs):
        self.resource = resource
        super().__init__(message, code="NOT_FOUND", **kwargs)


class UnauthorizedError(DomainException):
    """401 - Unauthorized"""

    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(message, code="UNAUTHORIZED", **kwargs)


class ForbiddenError(DomainException):
    """403 - Forbidden"""

    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(message, code="FORBIDDEN", **kwargs)


class ConflictError(DomainException):
    """409 - Resource conflict"""

    def __init__(self, message: str, resource: str = None, **kwargs):
        self.resource = resource
        super().__init__(message, code="CONFLICT", **kwargs)


class InternalServerError(DomainException):
    """500 - Internal server error"""

    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, code="INTERNAL_SERVER_ERROR", **kwargs)
