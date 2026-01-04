"""
Course-related enums.
"""
import enum


class CourseStatus(str, enum.Enum):
    """Course publication status"""

    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
