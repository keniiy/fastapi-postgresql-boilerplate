"""
Authentication routes.
Controllers are one-liners that call auth use cases.
Exceptions are handled globally by exception handlers.
Rate limiting is handled by global middleware.
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.common.schemas import AuthResponse, UserResponse
from app.domain.auth.use_cases.change_password import ChangePasswordUseCase
from app.domain.auth.use_cases.deactivate_account import DeactivateAccountUseCase
from app.domain.auth.use_cases.get_current_user import GetCurrentUserUseCase
from app.domain.auth.use_cases.login import LoginUseCase
from app.domain.auth.use_cases.logout import LogoutUseCase
from app.domain.auth.use_cases.refresh_token import RefreshTokenUseCase
from app.domain.auth.use_cases.register import RegisterUseCase
from app.domain.auth.use_cases.update_profile import UpdateProfileUseCase
from app.presentation.auth.dependencies import (
    get_change_password_use_case,
    get_current_user_id,
    get_current_user_use_case,
    get_deactivate_account_use_case,
    get_login_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
    get_register_use_case,
    get_update_profile_use_case,
)
from app.presentation.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest, use_case: RegisterUseCase = Depends(get_register_use_case)
) -> UserResponse:
    """Register a new user"""
    user = await use_case.execute(
        email=request.email, phone=request.phone, password=request.password
    )
    return UserResponse.model_validate({**user.__dict__, "role": user.role.value})


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest, use_case: LoginUseCase = Depends(get_login_use_case)
) -> AuthResponse:
    """Login user and return JWT tokens with user info"""
    user, tokens = await use_case.execute(
        email=request.email, phone=request.phone, password=request.password
    )
    return AuthResponse(
        user=UserResponse.model_validate({**user.__dict__, "role": user.role.value}), **tokens
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenResponse:
    """Refresh access token"""
    return TokenResponse(**await use_case.execute(request.refresh_token))


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> UserResponse:
    """Get current authenticated user profile"""
    user = await use_case.execute(user_id)
    return UserResponse.model_validate({**user.__dict__, "role": user.role.value})


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: UpdateProfileUseCase = Depends(get_update_profile_use_case),
) -> UserResponse:
    """Update current user profile"""
    user = await use_case.execute(user_id, email=request.email, phone=request.phone)
    return UserResponse.model_validate({**user.__dict__, "role": user.role.value})


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
):
    """Change user password"""
    await use_case.execute(user_id, request.current_password, request.new_password)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_account(
    user_id: int = Depends(get_current_user_id),
    use_case: DeactivateAccountUseCase = Depends(get_deactivate_account_use_case),
):
    """Deactivate current user account"""
    await use_case.execute(user_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    """Logout user"""
    await use_case.execute(credentials.credentials)
