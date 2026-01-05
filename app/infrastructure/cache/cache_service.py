"""
Cache service for application-level caching operations.
Provides a high-level API for caching with automatic serialization.
"""

import json
import logging
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from typing import Any, TypeVar

from redis.asyncio import Redis

from app.infrastructure.cache.redis_client import redis_client

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheService:
    """
    High-level caching service with JSON serialization.
    Gracefully handles Redis unavailability.
    """

    def __init__(self, redis: Redis | None = None, prefix: str = "app"):
        self._redis = redis
        self._prefix = prefix

    @property
    def redis(self) -> Redis | None:
        """Get Redis client (from injection or global)"""
        return self._redis or redis_client.client

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.
        Returns None if key doesn't exist or Redis unavailable.
        """
        if not self.redis:
            return None

        try:
            full_key = self._make_key(key)
            value = await self.redis.get(full_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        ttl_timedelta: timedelta | None = None,
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds
            ttl_timedelta: Time to live as timedelta

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False

        try:
            full_key = self._make_key(key)
            serialized = json.dumps(value, default=str)

            expire_seconds = None
            if ttl_timedelta:
                expire_seconds = int(ttl_timedelta.total_seconds())
            elif ttl:
                expire_seconds = ttl

            if expire_seconds:
                await self.redis.setex(full_key, expire_seconds, serialized)
            else:
                await self.redis.set(full_key, serialized)

            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False

        try:
            full_key = self._make_key(key)
            await self.redis.delete(full_key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        Returns count of deleted keys.
        """
        if not self.redis:
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = []
            async for key in self.redis.scan_iter(match=full_pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False

        try:
            full_key = self._make_key(key)
            return bool(await self.redis.exists(full_key))
        except Exception as e:
            logger.warning(f"Cache exists error for {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int | None:
        """Increment a counter in cache"""
        if not self.redis:
            return None

        try:
            full_key = self._make_key(key)
            return await self.redis.incrby(full_key, amount)
        except Exception as e:
            logger.warning(f"Cache increment error for {key}: {e}")
            return None

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int | None = None,
    ) -> Any | None:
        """
        Get value from cache, or compute and cache it.

        Args:
            key: Cache key
            factory: Async callable to compute value if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            return cached

        # Compute value
        if callable(factory):
            import asyncio

            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
        else:
            value = factory

        # Cache and return
        await self.set(key, value, ttl=ttl)
        return value


# Global cache service instance
_cache_service: CacheService | None = None


def get_cache_service() -> CacheService:
    """Get or create global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Callable[..., str] | None = None,
):
    """
    Decorator for caching function results.

    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds (default: 5 minutes)
        key_builder: Optional function to build cache key from args

    Example:
        @cached("user", ttl=60)
        async def get_user(user_id: int) -> User:
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cache = get_cache_service()

            # Build cache key
            if key_builder:
                key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Default: use all args as key
                key_parts = [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
                key = f"{key_prefix}:{':'.join(key_parts)}" if key_parts else key_prefix

            # Try cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value

            # Compute and cache
            logger.debug(f"Cache miss: {key}")
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl=ttl)
            return result

        return wrapper

    return decorator
