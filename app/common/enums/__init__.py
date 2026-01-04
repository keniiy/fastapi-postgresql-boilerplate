"""
Common enums used across the application.
All enum types should be defined here for reuse across layers.
Each domain/entity has its own file.
"""
from .user import UserRole
from .course import CourseStatus

__all__ = ["UserRole", "CourseStatus"]
