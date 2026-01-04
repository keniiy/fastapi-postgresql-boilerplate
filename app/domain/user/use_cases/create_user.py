"""
Create user use case.
"""
from typing import Optional
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository
from app.common.enums.user import UserRole
from app.common.exceptions import ValidationError, ConflictError
from datetime import datetime


class CreateUserUseCase:
    """Use case for creating a new user"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        password_hash: str = "",
        role: UserRole = UserRole.STUDENT,
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email (optional if phone provided)
            phone: User phone (optional if email provided)
            password_hash: Hashed password
            role: User role (default: STUDENT)

        Returns:
            Created User entity

        Raises:
            ValidationError: If email or phone not provided
            ConflictError: If user already exists
        """
        # Validate email or phone provided
        if not email and not phone:
            raise ValidationError(
                "Email or phone is required",
                field="email_or_phone",
                details={"email": email, "phone": phone},
            )

        # Check if user already exists
        if email:
            existing = await self.repository.get_by_email(email)
            if existing:
                raise ConflictError(
                    "User with this email already exists", resource="user", details={"email": email}
                )

        if phone:
            existing = await self.repository.get_by_phone(phone)
            if existing:
                raise ConflictError(
                    "User with this phone already exists", resource="user", details={"phone": phone}
                )

        # Create user entity
        user = User(
            id=None,
            email=email,
            phone=phone,
            role=role,
            is_active=True,
            created_at=datetime.now(),
            updated_at=None,
        )

        # Save via repository
        return await self.repository.create(user, password_hash)
