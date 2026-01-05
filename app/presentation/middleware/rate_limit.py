"""
Rate limiting middleware using slowapi.
Global rate limiting applied to all endpoints with per-endpoint overrides.
"""

from fastapi import status
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings

settings = get_settings()

# Initialize rate limiter with global default
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=(
        [settings.rate_limit_default] if settings.rate_limit_enabled else []
    ),  # Global default
    storage_uri=settings.rate_limit_storage,  # Use Redis in production: "redis://localhost:6379"
    headers_enabled=True,  # Add rate limit headers to responses
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply global rate limiting to all endpoints.
    Note: slowapi's decorators handle their own rate limiting.
    This middleware is a simple pass-through that allows decorators to work.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Continue with request - let decorators handle rate limiting
        response = await call_next(request)
        return response


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key - can be customized per endpoint"""
    # For authenticated endpoints, use user_id instead of IP
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    return get_remote_address(request)


# Rate limit decorator for use in routes
rate_limit = limiter.limit


# Rate limit exception handler
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors"""
    from fastapi.responses import JSONResponse

    from app.common.schemas.errors import ErrorResponse
    from app.presentation.middleware.trace_id import get_trace_id

    trace_id = get_trace_id(request)
    error_response = ErrorResponse(
        error="RateLimitExceeded",
        message="Rate limit exceeded. Please try again later.",
        code="RATE_LIMIT_EXCEEDED",
        path=str(request.url.path),
        trace_id=trace_id,
    )

    # Extract rate limit info from exception
    retry_after = getattr(exc, "retry_after", 60)

    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=error_response.model_dump(),
        headers={"X-Trace-ID": trace_id or "", "Retry-After": str(retry_after)},
    )

    return response


# Export RateLimitExceeded for use in other modules
__all__ = [
    "limiter",
    "rate_limit",
    "rate_limit_exception_handler",
    "RateLimitMiddleware",
    "RateLimitExceeded",
]
