from typing import Tuple
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.infrastructure.db.base.base_model import Base

settings = get_settings()


def _create_engine():
    """Create database engine with appropriate settings"""
    database_url = settings.database_url

    # Handle SQLite (for testing)
    if database_url.startswith("sqlite"):
        return create_async_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.db_echo,
        )

    # Handle PostgreSQL - convert to async driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1
        )

    return create_async_engine(
        database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        echo=settings.db_echo,
    )


engine = _create_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """
    Get a database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_database_type() -> str:
    """Get database type from connection URL"""
    database_url = settings.database_url
    if database_url.startswith("sqlite"):
        return "SQLite"
    elif database_url.startswith("postgresql"):
        return "PostgreSQL"
    return "Unknown"


async def check_database_connection() -> Tuple[bool, str]:
    """Check database connection and return status"""
    from sqlalchemy import text

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as e:
        return False, str(e)


async def init_db():
    """
    Initialize the database connection and create all tables.
    Import models here to ensure they're registered with Base.

    Note: This will fail gracefully if database is not available.
    In production, use Alembic migrations instead of create_all.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Import all models to register them with Base.metadata
    # This ensures all tables are created
    from app.infrastructure.db.user.model import User  # noqa: F401

    db_type = get_database_type()
    is_connected, connection_msg = await check_database_connection()

    if is_connected:
        logger.info(f"Database ({db_type}): Connected successfully")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info(f"Database ({db_type}): Tables initialized successfully")
        except Exception as e:
            logger.warning(f"Database ({db_type}): Failed to create tables: {e}")
    else:
        logger.warning(
            f"Database ({db_type}): Connection failed - {connection_msg}. "
            "App will start but database operations will fail. "
            "Use Alembic migrations in production."
        )
        # Don't raise - allow app to start even if DB is unavailable
