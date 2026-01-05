"""
Update profile use case.
"""

from app.common.exceptions import NotFoundError
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository
from app.domain.user.use_cases.get_user import GetUserByIdUseCase
from app.domain.user.use_cases.update_user import UpdateUserUseCase


class UpdateProfileUseCase:
    """Use case for updating user profile"""

    def __init__(self, user_repository: IUserRepository):
        self.get_by_id = GetUserByIdUseCase(user_repository)
        self.update_user = UpdateUserUseCase(user_repository)

    async def execute(
        self, user_id: int, email: str | None = None, phone: str | None = None
    ) -> User:
        """
        Update user profile.

        Args:
            user_id: User ID
            email: New email (optional)
            phone: New phone (optional)

        Returns:
            Updated User entity

        Raises:
            NotFoundError: If user not found
        """
        # Get user
        user = await self.get_by_id.execute(user_id)
        if not user:
            raise NotFoundError("User not found", resource="user", details={"user_id": user_id})

        # Update user
        return await self.update_user.execute(user=user, email=email, phone=phone)
