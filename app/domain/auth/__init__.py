"""
Auth domain module.
Contains auth-specific use cases.
"""
from .use_cases.register import RegisterUseCase
from .use_cases.login import LoginUseCase
from .use_cases.refresh_token import RefreshTokenUseCase
from .use_cases.get_current_user import GetCurrentUserUseCase
from .use_cases.update_profile import UpdateProfileUseCase
from .use_cases.change_password import ChangePasswordUseCase
from .use_cases.deactivate_account import DeactivateAccountUseCase
from .use_cases.logout import LogoutUseCase

__all__ = [
    "RegisterUseCase",
    "LoginUseCase",
    "RefreshTokenUseCase",
    "GetCurrentUserUseCase",
    "UpdateProfileUseCase",
    "ChangePasswordUseCase",
    "DeactivateAccountUseCase",
    "LogoutUseCase",
]

