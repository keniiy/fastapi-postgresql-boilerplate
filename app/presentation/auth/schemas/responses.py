"""
Authentication response schemas.
Re-exports common schemas and keeps auth-specific ones.
"""
from pydantic import BaseModel, ConfigDict
from app.common.schemas import AuthResponse, UserResponse

# Re-export common schemas for backward compatibility
__all__ = ["AuthResponse", "UserResponse", "TokenResponse"]


class TokenResponse(BaseModel):
    """JWT token response (for refresh token endpoint)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

