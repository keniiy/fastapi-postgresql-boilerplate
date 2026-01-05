"""
Register user use case.
"""
from typing import Optional

from app.common.enums.user import UserRole
from app.common.exceptions import ValidationError
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository
from app.domain.user.use_cases.create_user import CreateUserUseCase
from app.infrastructure.security.password import hash_password


class RegisterUseCase:
    """Use case for user registration"""

    def __init__(self, user_repository: IUserRepository):
        self.create_user = CreateUserUseCase(user_repository)

    async def execute(
        self, email: Optional[str] = None, phone: Optional[str] = None, password: str = ""
    ) -> User:
        """
        Register a new user.

        Args:
            email: User email (optional if phone provided)
            phone: User phone (optional if email provided)
            password: Plain password (will be hashed)

        Returns:
            User entity

        Raises:
            ValidationError: If password is empty
            ConflictError: If user already exists
        """
        # Validate password
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters", field="password")

        # Hash password using Argon2
        password_hash = hash_password(password)

        # Create user via user use case
        return await self.create_user.execute(
            email=email, phone=phone, password_hash=password_hash, role=UserRole.STUDENT
        )
