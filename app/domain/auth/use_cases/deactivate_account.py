"""
Deactivate account use case.
"""
from app.common.exceptions import NotFoundError
from app.domain.user.types.repository import IUserRepository
from app.domain.user.use_cases.deactivate_user import DeactivateUserUseCase
from app.domain.user.use_cases.get_user import GetUserByIdUseCase


class DeactivateAccountUseCase:
    """Use case for deactivating user account"""

    def __init__(self, user_repository: IUserRepository):
        self.get_by_id = GetUserByIdUseCase(user_repository)
        self.deactivate_user = DeactivateUserUseCase(user_repository)

    async def execute(self, user_id: int) -> None:
        """
        Deactivate user account.

        Args:
            user_id: User ID

        Raises:
            NotFoundError: If user not found
        """
        # Get user
        user = await self.get_by_id.execute(user_id)
        if not user:
            raise NotFoundError("User not found", resource="user", details={"user_id": user_id})

        # Deactivate user
        await self.deactivate_user.execute(user)
