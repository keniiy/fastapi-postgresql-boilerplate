"""
User domain entity - pure business object.
No database dependencies, just business logic.
"""

from dataclasses import dataclass
from datetime import datetime

from app.common.enums.user import UserRole


@dataclass
class User:
    """
    User domain entity.
    Represents a user in the business domain.
    """

    id: int | None
    email: str | None
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    def can_create_course(self) -> bool:
        """Business rule: only instructors and admins can create courses"""
        return self.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]

    def can_enroll(self) -> bool:
        """Business rule: only students can enroll in courses"""
        return self.role == UserRole.STUDENT

    def can_manage_course(self, course_owner_id: int) -> bool:
        """Business rule: can manage course if owner or admin"""
        return self.id == course_owner_id or self.role == UserRole.ADMIN

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    def is_instructor(self) -> bool:
        """Check if user is instructor"""
        return self.role == UserRole.INSTRUCTOR

    def is_student(self) -> bool:
        """Check if user is student"""
        return self.role == UserRole.STUDENT
