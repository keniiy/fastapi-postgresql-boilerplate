"""
Structured error response schemas.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Single error detail"""

    field: str | None = None
    message: str
    code: str | None = None
    value: Any | None = None


class ErrorResponse(BaseModel):
    """Standard error response format"""

    error: str = Field(..., description="Error type/class name")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Error code for programmatic handling")
    details: list[ErrorDetail] | None = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    path: str | None = Field(None, description="Request path")
    trace_id: str | None = Field(None, description="Request trace ID for observability")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ValidationError",
                "message": "Email or phone is required",
                "code": "VALIDATION_ERROR",
                "details": [
                    {
                        "field": "email",
                        "message": "Email is required when phone is not provided",
                        "code": "REQUIRED_FIELD",
                    }
                ],
                "timestamp": "2024-01-01T00:00:00Z",
                "path": "/api/v1/auth/register",
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }
