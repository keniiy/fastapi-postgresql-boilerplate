"""
Get user use cases.
"""
from typing import Optional
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository


class GetUserByIdUseCase:
    """Use case for getting user by ID"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.repository.get_by_id(user_id)


class GetUserByEmailUseCase:
    """Use case for getting user by email"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.repository.get_by_email(email)


class GetUserByPhoneUseCase:
    """Use case for getting user by phone"""

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def execute(self, phone: str) -> Optional[User]:
        """Get user by phone"""
        return await self.repository.get_by_phone(phone)
