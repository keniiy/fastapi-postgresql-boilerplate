"""
User repository - database operations for User model.
Implements data access layer for users.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils.pagination import PaginatedResponse, PaginationParams
from app.infrastructure.db.base.base_repository import BaseRepository
from app.infrastructure.db.user.model import User


class UserRepository(BaseRepository[User]):
    """
    User repository with user-specific database operations.
    Extends BaseRepository with common CRUD + user-specific methods.
    Uses base repository methods where possible.
    """

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, db: AsyncSession, phone: str) -> User | None:
        """Get user by phone"""
        result = await db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_by_email_or_phone(
        self, db: AsyncSession, email: str | None = None, phone: str | None = None
    ) -> User | None:
        """Get user by email or phone"""
        if email:
            return await self.get_by_email(db, email)
        elif phone:
            return await self.get_by_phone(db, phone)
        return None

    async def deactivate(self, db: AsyncSession, user: User) -> User:
        """Soft delete user (set is_active to False) - uses base update method"""
        user.is_active = False
        return await self.update(db, user)

    async def get_all_active(
        self, db: AsyncSession, skip: int = 0, limit: int | None = None
    ) -> list[User]:
        """
        Get all active users.
        Can be used with or without pagination (limit=None returns all).
        """
        query = select(User).where(User.is_active).offset(skip)
        if limit is not None:
            query = query.limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_active_paginated(
        self, db: AsyncSession, pagination: PaginationParams
    ) -> PaginatedResponse[User]:
        """
        Get all active users with pagination and metadata.
        Returns proper pagination response for frontend.
        """
        # Get total count of active users
        total = await self._count_active(db)

        # Get paginated items
        items = await self.get_all_active(db, skip=pagination.skip, limit=pagination.limit)

        # Create metadata
        from app.common.utils.pagination import PaginationMeta

        meta = PaginationMeta.create(
            total=total, page=pagination.page, page_size=pagination.page_size
        )

        return PaginatedResponse(items=items, meta=meta)

    async def get_all_active_with_count(
        self, db: AsyncSession, skip: int = 0, limit: int | None = None
    ) -> tuple[list[User], int]:
        """
        Get all active users with total count.
        Useful when you need both data and count in one call.
        """
        # Get total count
        total = await self._count_active(db)

        # Get items
        items = await self.get_all_active(db, skip=skip, limit=limit)

        return items, total

    async def get_by_role(
        self, db: AsyncSession, role: str, skip: int = 0, limit: int | None = None
    ) -> list[User]:
        """
        Get users by role.
        Can be used with or without pagination (limit=None returns all).
        """
        query = select(User).where(User.role == role).where(User.is_active).offset(skip)
        if limit is not None:
            query = query.limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_role_paginated(
        self, db: AsyncSession, role: str, pagination: PaginationParams
    ) -> PaginatedResponse[User]:
        """
        Get users by role with pagination and metadata.
        Returns proper pagination response for frontend.
        """
        # Get total count
        total = await self._count_by_role(db, role)

        # Get paginated items
        items = await self.get_by_role(db, role=role, skip=pagination.skip, limit=pagination.limit)

        # Create metadata
        from app.common.utils.pagination import PaginationMeta

        meta = PaginationMeta.create(
            total=total, page=pagination.page, page_size=pagination.page_size
        )

        return PaginatedResponse(items=items, meta=meta)

    async def get_by_role_with_count(
        self, db: AsyncSession, role: str, skip: int = 0, limit: int | None = None
    ) -> tuple[list[User], int]:
        """
        Get users by role with total count.
        """
        # Get total count
        total = await self._count_by_role(db, role)

        # Get items
        items = await self.get_by_role(db, role=role, skip=skip, limit=limit)

        return items, total

    # Private helper methods
    async def _count_active(self, db: AsyncSession) -> int:
        """Count active users"""
        result = await db.execute(select(func.count()).select_from(User).where(User.is_active))
        return result.scalar() or 0

    async def _count_by_role(self, db: AsyncSession, role: str) -> int:
        """Count users by role"""
        result = await db.execute(
            select(func.count()).select_from(User).where(User.role == role).where(User.is_active)
        )
        return result.scalar() or 0
