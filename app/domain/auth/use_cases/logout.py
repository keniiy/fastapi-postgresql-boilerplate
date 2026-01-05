"""
Logout use case.

Note: In a stateless JWT architecture, logout is typically handled client-side
by removing the token. If token blacklisting is required, implement a token
blacklist service (e.g., Redis) and add tokens to it here.
"""

from app.common.exceptions import UnauthorizedError
from app.infrastructure.security.jwt import decode_token


class LogoutUseCase:
    """
    Use case for user logout.

    In a stateless JWT system, logout is handled client-side by discarding tokens.
    This use case validates the token format. For token blacklisting, implement
    a blacklist service (Redis recommended) and add tokens here.
    """

    async def execute(self, token: str) -> None:
        """
        Logout user (validate token format).

        Args:
            token: Access token to validate

        Raises:
            UnauthorizedError: If token is invalid or expired
        """
        # Validate token format and expiration
        payload = decode_token(token)
        if not payload:
            raise UnauthorizedError("Invalid or expired token")

        # In a stateless JWT system, logout is handled client-side.
        # The client should discard the token.
        #
        # If token blacklisting is required:
        # 1. Implement a token blacklist service (Redis recommended)
        # 2. Add token to blacklist with TTL matching token expiration
        # 3. Check blacklist in JWT validation middleware
        #
        # Example:
        # await blacklist_service.add(token, ttl=settings.access_token_expire_minutes * 60)

        # Token is valid - logout successful (client should discard token)
        return
