"""
Trace ID middleware for request tracing and observability.
Generates unique trace IDs for each request and attaches them to request state and context.
"""
import uuid
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.common.utils.logging import get_trace_id as get_trace_id_from_context
from app.common.utils.logging import set_trace_id


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and attach trace IDs to requests"""

    async def dispatch(self, request: Request, call_next):
        # Check if trace ID is provided in headers (for distributed tracing)
        trace_id = request.headers.get("X-Trace-ID") or request.headers.get("X-Request-ID")

        # Generate new trace ID if not provided
        if not trace_id:
            trace_id = str(uuid.uuid4())

        # Attach trace ID to request state
        request.state.trace_id = trace_id

        # Set trace ID in context for global access in logging
        set_trace_id(trace_id)

        try:
            # Process request
            response = await call_next(request)
        finally:
            # Clear trace ID from context after request
            set_trace_id(None)

        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Request-ID"] = trace_id

        return response


def get_trace_id(request: Request) -> Optional[str]:
    """
    Get trace ID from request state (for backward compatibility).

    For new code, use app.common.utils.logging.get_trace_id() instead.
    """
    return getattr(request.state, "trace_id", None) or get_trace_id_from_context()
