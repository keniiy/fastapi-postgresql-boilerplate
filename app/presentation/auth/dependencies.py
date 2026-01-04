"""
Dependencies for auth routes.
Provides dependency injection for auth use cases.
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.config import get_db
from app.infrastructure.db.user.adapter import UserRepositoryAdapter
from app.infrastructure.security.jwt import get_user_id_from_token
from app.common.exceptions import UnauthorizedError
from app.domain.auth.use_cases.register import RegisterUseCase
from app.domain.auth.use_cases.login import LoginUseCase
from app.domain.auth.use_cases.refresh_token import RefreshTokenUseCase
from app.domain.auth.use_cases.get_current_user import GetCurrentUserUseCase
from app.domain.auth.use_cases.update_profile import UpdateProfileUseCase
from app.domain.auth.use_cases.change_password import ChangePasswordUseCase
from app.domain.auth.use_cases.deactivate_account import DeactivateAccountUseCase
from app.domain.auth.use_cases.logout import LogoutUseCase

security = HTTPBearer()


# Repository adapter dependency
def get_user_repository_adapter(db: AsyncSession = Depends(get_db)) -> UserRepositoryAdapter:
    """Get user repository adapter instance"""
    return UserRepositoryAdapter(db)


# Auth use case dependencies
def get_register_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> RegisterUseCase:
    """Get register use case"""
    return RegisterUseCase(repository)


def get_login_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> LoginUseCase:
    """Get login use case"""
    return LoginUseCase(repository)


def get_refresh_token_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> RefreshTokenUseCase:
    """Get refresh token use case"""
    return RefreshTokenUseCase(repository)


def get_current_user_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> GetCurrentUserUseCase:
    """Get current user use case"""
    return GetCurrentUserUseCase(repository)


def get_update_profile_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> UpdateProfileUseCase:
    """Get update profile use case"""
    return UpdateProfileUseCase(repository)


def get_change_password_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> ChangePasswordUseCase:
    """Get change password use case"""
    return ChangePasswordUseCase(repository)


def get_deactivate_account_use_case(
    repository: UserRepositoryAdapter = Depends(get_user_repository_adapter),
) -> DeactivateAccountUseCase:
    """Get deactivate account use case"""
    return DeactivateAccountUseCase(repository)


def get_logout_use_case() -> LogoutUseCase:
    """Get logout use case"""
    return LogoutUseCase()


# Authentication dependency
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from JWT token"""
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise UnauthorizedError("Invalid or expired token")
    return user_id
