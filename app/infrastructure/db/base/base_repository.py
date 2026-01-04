"""
Abstract base repository with common CRUD operations.
All repositories should inherit from this.
"""
from abc import ABC
from typing import Generic, TypeVar, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.infrastructure.db.base.base_model import Base
from app.common.utils.pagination import PaginationParams, PaginatedResponse

# TypeVar for generic repository pattern
# ModelType must be a class that inherits from Base
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract base repository with common database operations.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self):
                super().__init__(User)
    """

    def __init__(self, model: type[ModelType]):
        """
        Initialize repository with a model class.

        Args:
            model: The SQLAlchemy model class (e.g., User, Course)
        """
        self.model = model

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            db: Database session
            obj: Model instance to create

        Returns:
            Created model instance with generated fields (e.g., id)
        """
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Get a record by its ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance if found, None otherwise
        """
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        result = await db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_paginated(
        self,
        db: AsyncSession,
        pagination: PaginationParams
    ) -> PaginatedResponse[ModelType]:
        """
        Get all records with pagination and metadata.

        Args:
            db: Database session
            pagination: Pagination parameters

        Returns:
            PaginatedResponse with items and metadata
        """
        # Get total count
        total = await self.count(db)

        # Get paginated items
        items = await self.get_all(db, skip=pagination.skip, limit=pagination.limit)

        # Create metadata
        from app.common.utils.pagination import PaginationMeta
        meta = PaginationMeta.create(
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )

        return PaginatedResponse(items=items, meta=meta)

    async def get_all_with_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> Tuple[List[ModelType], int]:
        """
        Get all records with total count.
        Useful when you need both data and count in one call.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (None = no limit)

        Returns:
            Tuple of (items, total_count)
        """
        # Get total count
        total = await self.count(db)

        # Build query
        query = select(self.model).offset(skip)
        if limit is not None:
            query = query.limit(limit)

        # Get items
        result = await db.execute(query)
        items = result.scalars().all()

        return items, total

    async def update(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            obj: Model instance with updated values (must have id)

        Returns:
            Updated model instance
        """
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID to delete

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get_by_id(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False

    async def count(self, db: AsyncSession) -> int:
        """
        Count total number of records.

        Args:
            db: Database session

        Returns:
            Total count of records
        """
        result = await db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
