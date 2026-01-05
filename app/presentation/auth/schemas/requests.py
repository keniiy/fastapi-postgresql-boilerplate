"""
Authentication request schemas.
All incoming request models for auth endpoints.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    """User registration request"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Password must be 8-128 characters"
    )

    @model_validator(mode="after")
    def validate_email_or_phone(self):
        """Ensure at least email or phone is provided"""
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "+1234567890",
                "password": "securepassword123",
            }
        }


class LoginRequest(BaseModel):
    """User login request"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    password: str = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_email_or_phone(self):
        """Ensure at least email or phone is provided"""
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        return self

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "securepassword123"}
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }


class ChangePasswordRequest(BaseModel):
    """Change password request"""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password must be 8-128 characters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword123",
            }
        }


class UpdateProfileRequest(BaseModel):
    """Update user profile request"""

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        """Ensure at least one field is provided"""
        if not self.email and not self.phone:
            raise ValueError("At least email or phone must be provided")
        return self

    class Config:
        json_schema_extra = {"example": {"email": "newemail@example.com", "phone": "+1234567890"}}
