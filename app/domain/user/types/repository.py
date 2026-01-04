"""
User repository interface.
Defines the contract for user data access operations.
Implementation is in infrastructure layer.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.domain.user.entities.user import User


class IUserRepository(ABC):
    """Interface for user repository operations"""

    @abstractmethod
    async def create(self, user: User, password_hash: str = "") -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone"""
        pass

    @abstractmethod
    async def get_by_email_with_password(self, email: str) -> Optional[Tuple[User, str]]:
        """Get user by email with password hash for authentication"""
        pass

    @abstractmethod
    async def get_by_phone_with_password(self, phone: str) -> Optional[Tuple[User, str]]:
        """Get user by phone with password hash for authentication"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass

    @abstractmethod
    async def update_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password"""
        pass

    @abstractmethod
    async def deactivate(self, user: User) -> User:
        """Deactivate user (soft delete)"""
        pass

