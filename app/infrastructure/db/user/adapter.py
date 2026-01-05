"""
Repository adapter - bridges infrastructure repository with domain interface.
Converts between SQLAlchemy models and domain entities.
This is infrastructure concern - adapting infrastructure to domain.
"""
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums.user import UserRole
from app.domain.user.entities.user import User
from app.domain.user.types.repository import IUserRepository
from app.infrastructure.db.user.model import User as UserModel
from app.infrastructure.db.user.repository import UserRepository as InfraUserRepository


class UserRepositoryAdapter(IUserRepository):
    """Adapter that implements IUserRepository using infrastructure repository"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._repo = InfraUserRepository()

    def _model_to_entity(self, model: UserModel) -> Optional[User]:
        """Convert SQLAlchemy model to domain entity"""
        if not model:
            return None
        return User(
            id=model.id,
            email=model.email,
            phone=model.phone,
            role=UserRole(model.role.value) if model.role else UserRole.STUDENT,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, user: User, password_hash: str = "") -> User:
        """Create a new user"""
        model = UserModel(
            email=user.email,
            phone=user.phone,
            password_hash=password_hash,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        created = await self._repo.create(self.db, model)
        return self._model_to_entity(created)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        model = await self._repo.get_by_id(self.db, user_id)
        return self._model_to_entity(model)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        model = await self._repo.get_by_email(self.db, email)
        return self._model_to_entity(model)

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone"""
        model = await self._repo.get_by_phone(self.db, phone)
        return self._model_to_entity(model)

    async def get_by_email_with_password(self, email: str) -> Optional[Tuple[User, str]]:
        """Get user by email with password hash for authentication"""
        model = await self._repo.get_by_email(self.db, email)
        if not model:
            return None
        return self._model_to_entity(model), model.password_hash

    async def get_by_phone_with_password(self, phone: str) -> Optional[Tuple[User, str]]:
        """Get user by phone with password hash for authentication"""
        model = await self._repo.get_by_phone(self.db, phone)
        if not model:
            return None
        return self._model_to_entity(model), model.password_hash

    async def update(self, user: User) -> User:
        """Update user"""
        # Get existing model
        model = await self._repo.get_by_id(self.db, user.id)
        if not model:
            raise ValueError("User not found")

        # Update fields
        model.email = user.email
        model.phone = user.phone
        model.role = user.role
        model.is_active = user.is_active
        model.updated_at = user.updated_at

        updated = await self._repo.update(self.db, model)
        return self._model_to_entity(updated)

    async def update_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password"""
        model = await self._repo.get_by_id(self.db, user_id)
        if not model:
            return False

        model.password_hash = password_hash
        model.updated_at = datetime.now()
        await self._repo.update(self.db, model)
        return True

    async def deactivate(self, user: User) -> User:
        """Deactivate user"""
        model = await self._repo.get_by_id(self.db, user.id)
        if not model:
            raise ValueError("User not found")

        deactivated = await self._repo.deactivate(self.db, model)
        return self._model_to_entity(deactivated)
