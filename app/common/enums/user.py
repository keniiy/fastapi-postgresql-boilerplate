"""
User-related enums.
"""

import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""

    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"
