"""
Pagination utilities and response models.
"""
from typing import Generic, TypeVar, List, Any
from pydantic import BaseModel, ConfigDict
from dataclasses import dataclass

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    skip: int | None = None
    limit: int | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate skip/limit from page/page_size if not provided
        if self.skip is None:
            self.skip = (self.page - 1) * self.page_size
        if self.limit is None:
            self.limit = self.page_size


class PaginationMeta(BaseModel):
    """Pagination metadata for frontend"""
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationMeta":
        """Create pagination metadata"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


@dataclass
class PaginatedResponse(Generic[T]):
    """
    Paginated response with data and metadata.
    Uses dataclass instead of Pydantic to avoid type conflicts with SQLAlchemy models.
    """
    items: List[T]
    meta: PaginationMeta

