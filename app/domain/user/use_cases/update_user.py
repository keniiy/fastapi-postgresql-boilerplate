"""
Update user use case.
"""
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository
from datetime import datetime


class UpdateUserUseCase:
    """Use case for updating user"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(
        self,
        user: User,
        email: str | None = None,
        phone: str | None = None,
        role: str | None = None
    ) -> User:
        """
        Update user information.

        Args:
            user: User entity to update
            email: New email (optional)
            phone: New phone (optional)
            role: New role (optional)

        Returns:
            Updated User entity
        """
        # Update fields if provided
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone
        if role is not None:
            from app.common.enums.user import UserRole
            user.role = UserRole(role)

        # Update timestamp
        user.updated_at = datetime.now()

        # Save via repository
        return await self.repository.update(user)

