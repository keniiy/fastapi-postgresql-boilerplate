"""
User domain module.
Contains entities, types (interfaces), and use cases for user domain.
"""
from .entities import User
from .types import IUserRepository
from .use_cases import (
    CreateUserUseCase,
    DeactivateUserUseCase,
    GetUserByEmailUseCase,
    GetUserByIdUseCase,
    GetUserByPhoneUseCase,
    UpdateUserUseCase,
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
