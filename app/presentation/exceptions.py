"""
Comprehensive exception handlers for all error types.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, Type

from app.common.exceptions import (
    DomainException,
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    InternalServerError
)
from app.common.schemas.errors import ErrorResponse, ErrorDetail
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Map domain exceptions to HTTP status codes
EXCEPTION_STATUS_MAP: Dict[Type[DomainException], int] = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
    InternalServerError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def create_error_response(
    error: str,
    message: str,
    code: str,
    status_code: int,
    request: Request,
    details: list = None
) -> JSONResponse:
    """Create standardized error response"""
    from app.common.utils.logging import get_trace_id

    trace_id = get_trace_id()
    error_response = ErrorResponse(
        error=error,
        message=message,
        code=code,
        details=details,
        path=str(request.url.path),
        trace_id=trace_id
    )

    response = JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )

    # Add trace ID to response headers
    if trace_id:
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Request-ID"] = trace_id

    return response


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle domain exceptions with full error details"""
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)

    # Build details list
    details = []
    if isinstance(exc, ValidationError) and exc.field:
        details.append(ErrorDetail(
            field=exc.field,
            message=exc.message,
            code=exc.code
        ))
    elif isinstance(exc, NotFoundError) and exc.resource:
        details.append(ErrorDetail(
            message=exc.message,
            code=exc.code,
            value=exc.resource
        ))
    elif exc.details:
        for key, value in exc.details.items():
            details.append(ErrorDetail(
                field=key,
                message=str(value),
                code=exc.code
            ))

    # Log error with trace ID (automatically included via logging filter)
    from app.common.utils.logging import get_trace_id
    logger.warning(
        f"Domain exception: {exc.__class__.__name__} - {exc.message}",
        extra={"path": request.url.path, "code": exc.code}
    )

    return create_error_response(
        error=exc.__class__.__name__,
        message=exc.message,
        code=exc.code,
        status_code=status_code,
        request=request,
        details=details if details else None
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors with detailed field errors"""
    details = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append(ErrorDetail(
            field=field_path or "body",
            message=error["msg"],
            code=error["type"],
            value=error.get("input")
        ))

    from app.common.utils.logging import get_trace_id
    logger.warning(
        f"Validation error: {len(details)} field(s) failed",
        extra={"path": request.url.path, "details": details}
    )

    return create_error_response(
        error="ValidationError",
        message="Request validation failed",
        code="VALIDATION_ERROR",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request=request,
        details=details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions - safety net"""
    # Log full error in development, generic in production (trace ID automatically included)
    if settings.debug:
        logger.exception(
            f"Unexpected error: {exc}",
            exc_info=exc
        )
        message = str(exc)
    else:
        logger.error(
            f"Unexpected error: {type(exc).__name__}"
        )
        message = "An unexpected error occurred"

    return create_error_response(
        error="InternalServerError",
        message=message,
        code="INTERNAL_SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request=request
    )

