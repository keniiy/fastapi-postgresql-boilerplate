"""
Deactivate user use case.
"""
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository


class DeactivateUserUseCase:
    """Use case for deactivating user (soft delete)"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, user: User) -> User:
        """
        Deactivate a user (soft delete).

        Args:
            user: User entity to deactivate

        Returns:
            Deactivated User entity
        """
        return await self.repository.deactivate(user)

