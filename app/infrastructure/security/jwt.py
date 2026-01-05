"""
JWT token utilities for encoding and decoding tokens.
"""

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings

settings = get_settings()


def create_access_token(user_id: int, role: str) -> str:
    """Create JWT access token"""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token"""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(user_id), "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> int | None:
    """Extract user ID from JWT token"""
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return int(payload.get("sub"))
    return None
