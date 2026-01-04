"""
User domain module.
Contains entities, types (interfaces), and use cases for user domain.
"""
from .entities import User
from .types import IUserRepository
from .use_cases import (
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    GetUserByPhoneUseCase,
    UpdateUserUseCase,
    DeactivateUserUseCase,
)

__all__ = [
    "User",
    "IUserRepository",
    "CreateUserUseCase",
    "GetUserByIdUseCase",
    "GetUserByEmailUseCase",
    "GetUserByPhoneUseCase",
    "UpdateUserUseCase",
    "DeactivateUserUseCase",
]
