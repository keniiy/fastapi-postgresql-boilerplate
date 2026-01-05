"""
Common enums used across the application.
All enum types should be defined here for reuse across layers.
Each domain/entity has its own file.
"""
from .course import CourseStatus
from .user import UserRole

__all__ = ["UserRole", "CourseStatus"]
