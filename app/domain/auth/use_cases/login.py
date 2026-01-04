"""
Login user use case.
"""
from typing import Optional, Dict, Tuple
from app.domain.user.types.repository import IUserRepository
from app.domain.user.entities.user import User
from app.common.exceptions import ValidationError, UnauthorizedError
from app.infrastructure.security.password import verify_password
from app.infrastructure.security.jwt import create_access_token, create_refresh_token


class LoginUseCase:
    """Use case for user login"""

    def __init__(self, user_repository: IUserRepository):
        self.repository = user_repository

    async def execute(
        self, email: Optional[str] = None, phone: Optional[str] = None, password: str = ""
    ) -> Tuple[User, Dict[str, str]]:
        """
        Login user and return user + tokens.

        Args:
            email: User email (optional if phone provided)
            phone: User phone (optional if email provided)
            password: User password

        Returns:
            Tuple of (User entity, tokens dict with access_token, refresh_token, token_type)

        Raises:
            ValidationError: If email or phone not provided
            UnauthorizedError: If credentials are invalid or account is deactivated
        """
        # Validate input
        if not email and not phone:
            raise ValidationError("Email or phone is required", field="credentials")

        # Get user with password hash
        result = None
        if email:
            result = await self.repository.get_by_email_with_password(email)
        elif phone:
            result = await self.repository.get_by_phone_with_password(phone)

        if not result:
            raise UnauthorizedError("Invalid credentials")

        user, password_hash = result

        # Verify password
        if not verify_password(password, password_hash):
            raise UnauthorizedError("Invalid credentials")

        # Check if account is active
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Generate JWT tokens
        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)

        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

        return user, tokens
