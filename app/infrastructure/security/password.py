"""
Password hashing utilities using Argon2.
Argon2 is the winner of the Password Hashing Competition (PHC).
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Initialize hasher with secure defaults
_hasher = PasswordHasher(
    time_cost=2,  # Number of iterations
    memory_cost=65536,  # 64MB memory usage
    parallelism=1,  # Number of parallel threads
    hash_len=32,  # Length of the hash
    salt_len=16,  # Length of the salt
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password to verify
        password_hash: Stored password hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        _hasher.verify(password_hash, password)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Check if a password hash needs to be rehashed.
    Useful when upgrading hash parameters.

    Args:
        password_hash: Stored password hash

    Returns:
        True if rehash is needed, False otherwise
    """
    return _hasher.check_needs_rehash(password_hash)
