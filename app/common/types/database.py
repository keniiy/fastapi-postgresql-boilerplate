"""
Database-related type definitions.
"""
from typing import TypeVar
from app.infrastructure.db.base.base_model import Base

# Generic type for database models
ModelType = TypeVar("ModelType", bound=Base)

