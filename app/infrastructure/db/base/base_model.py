"""
Base model for all SQLAlchemy models.
All database models should inherit from this Base.
"""

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# Create the declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields.
    All models should inherit from this for audit fields.
    """

    __abstract__ = True  # This means SQLAlchemy won't create a table for this

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
