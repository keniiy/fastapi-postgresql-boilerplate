"""
Get current user use case.
"""
from app.domain.user.use_cases.get_user import GetUserByIdUseCase
from app.domain.user.types.repository import IUserRepository
from app.domain.user.entities.user import User
from app.common.exceptions import NotFoundError


class GetCurrentUserUseCase:
    """Use case for getting current authenticated user"""

    def __init__(self, user_repository: IUserRepository):
        self.get_by_id = GetUserByIdUseCase(user_repository)

    async def execute(self, user_id: int) -> User:
        """
        Get current user profile.

        Args:
            user_id: Current user ID from JWT token

        Returns:
            User entity

        Raises:
            NotFoundError: If user not found
        """
        user = await self.get_by_id.execute(user_id)

        if not user:
            raise NotFoundError(
                "User not found",
                resource="user",
                details={"user_id": user_id}
            )

        return user

