"""
Refresh token use case.
"""
from typing import Dict

from app.common.exceptions import UnauthorizedError
from app.domain.user.types.repository import IUserRepository
from app.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token


class RefreshTokenUseCase:
    """Use case for refreshing access token"""

    def __init__(self, user_repository: IUserRepository):
        self.repository = user_repository

    async def execute(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            Dict with access_token, refresh_token, token_type

        Raises:
            UnauthorizedError: If token is invalid or user not found/inactive
        """
        # Decode and verify refresh token
        payload = decode_token(refresh_token)

        if not payload:
            raise UnauthorizedError("Invalid or expired refresh token")

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        # Extract user ID
        user_id = int(payload.get("sub"))

        # Fetch user to get current role and verify account is still active
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise UnauthorizedError("User not found")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Generate new tokens with current role
        new_access_token = create_access_token(user_id, user.role.value)
        new_refresh_token = create_refresh_token(user_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
