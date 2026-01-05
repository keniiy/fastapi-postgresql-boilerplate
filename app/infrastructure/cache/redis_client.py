"""
Redis client configuration and connection management.
"""
import logging
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisClient:
    """
    Redis client wrapper with connection management.
    Provides async context manager for safe connection handling.
    """

    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.redis_url
        self._client: Optional[Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None

    async def connect(self) -> None:
        """Initialize Redis connection pool"""
        if self._client is not None:
            return

        try:
            self._pool = redis.ConnectionPool.from_url(
                self.url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            self._client = Redis(connection_pool=self._pool)

            # Test connection
            await self._client.ping()
            logger.info(f"Redis connected: {self._mask_url(self.url)}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self._client = None
            self._pool = None

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis disconnected")

    @property
    def client(self) -> Optional[Redis]:
        """Get the Redis client instance"""
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._client is not None

    async def health_check(self) -> tuple[bool, str]:
        """Check Redis health"""
        if not self._client:
            return False, "Not connected"
        try:
            await self._client.ping()
            return True, "Connected"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask password in URL for logging"""
        if "@" in url:
            parts = url.split("@")
            return f"redis://***@{parts[-1]}"
        return url


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> Optional[Redis]:
    """
    Dependency injection for Redis client.
    Returns None if Redis is not available (graceful degradation).
    """
    return redis_client.client


@asynccontextmanager
async def redis_connection():
    """
    Async context manager for Redis connection lifecycle.
    Use this in lifespan events.
    """
    await redis_client.connect()
    try:
        yield redis_client
    finally:
        await redis_client.disconnect()
