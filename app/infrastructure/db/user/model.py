"""
User database model - SQLAlchemy model for users table.
"""
from sqlalchemy import Column, String, Boolean, Enum
from app.infrastructure.db.base.base_model import BaseModel
from app.common import UserRole


class User(BaseModel):
    """
    User database model.
    Represents the 'users' table in the database.
    """
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"

