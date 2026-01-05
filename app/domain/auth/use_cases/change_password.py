"""
Change password use case.
"""

from app.common.exceptions import NotFoundError, UnauthorizedError, ValidationError
from app.domain.user.types.repository import IUserRepository
from app.infrastructure.security.password import hash_password, verify_password


class ChangePasswordUseCase:
    """Use case for changing user password"""

    def __init__(self, user_repository: IUserRepository):
        self.repository = user_repository

    async def execute(self, user_id: int, current_password: str, new_password: str) -> None:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Raises:
            NotFoundError: If user not found
            UnauthorizedError: If current password is incorrect
            ValidationError: If validation fails
        """
        # Validate new password
        if not new_password or len(new_password) < 8:
            raise ValidationError(
                "New password must be at least 8 characters", field="new_password"
            )

        # Get user with password - we need email or phone to get password
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found", resource="user", details={"user_id": user_id})

        # Get password hash via email or phone
        result = None
        if user.email:
            result = await self.repository.get_by_email_with_password(user.email)
        elif user.phone:
            result = await self.repository.get_by_phone_with_password(user.phone)

        if not result:
            raise NotFoundError("User not found", resource="user")

        _, current_hash = result

        # Verify current password
        if not verify_password(current_password, current_hash):
            raise UnauthorizedError("Current password is incorrect")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password in database
        await self.repository.update_password(user_id, new_password_hash)
