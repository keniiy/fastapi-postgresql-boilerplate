from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.common.exceptions import DomainException
from app.common.utils.logging import setup_logging
from app.core.config import get_settings
from app.infrastructure.db.config import init_db
from app.presentation.auth import router as auth_router
from app.presentation.exceptions import (
    domain_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.presentation.middleware.rate_limit import (
    RateLimitExceeded,
    RateLimitMiddleware,
    limiter,
    rate_limit_exception_handler,
)
from app.presentation.middleware.trace_id import TraceIDMiddleware

# Load environment variables
load_dotenv()

settings = get_settings()

# Configure logging on startup
setup_logging(log_level=settings.log_level, json_format=settings.log_json_format)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    import logging

    from app.infrastructure.cache.redis_client import redis_client

    logger = logging.getLogger(__name__)

    # Startup banner
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {app.title} v{app.version}")
    logger.info(f"📍 Environment: {settings.environment.upper()}")
    logger.info("=" * 70)

    # Initialize database (logs its own status)
    await init_db()

    # Initialize Redis
    await redis_client.connect()
    redis_ok, redis_msg = await redis_client.health_check()
    if redis_ok:
        logger.info(f"Redis: {redis_msg}")
    else:
        logger.warning(f"Redis: {redis_msg} (caching disabled)")

    # Log API documentation links
    logger.info("=" * 70)
    logger.info("📚 API Documentation:")
    logger.info("   Swagger UI:  http://localhost:8000/docs")
    logger.info("   ReDoc:       http://localhost:8000/redoc")
    logger.info("   OpenAPI:     http://localhost:8000/openapi.json")
    logger.info("=" * 70)
    logger.info("✅ Application startup complete!")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("Application shutdown initiated")
    await redis_client.disconnect()


app = FastAPI(
    title="FastAPI Clean Architecture Boilerplate",
    description="""
    Production-ready FastAPI application template following Clean Architecture principles,
    Domain-Driven Design (DDD), and industry best practices.

    ## Features

    * **Clean Architecture**: Clear separation of concerns (Presentation, Domain, Infrastructure)
    * **Async/Await**: Full async support with SQLAlchemy 2.0
    * **Authentication**: JWT-based authentication with access & refresh tokens
    * **Security**: Password hashing with Argon2, rate limiting, CORS support
    * **Observability**: Request trace IDs, structured logging
    * **Database**: PostgreSQL with asyncpg driver
    * **Testing**: Pytest with async support, SQLite in-memory for tests

    ## API Documentation

    * **Swagger UI**: Interactive API documentation at `/docs`
    * **ReDoc**: Alternative documentation at `/redoc`
    * **OpenAPI**: JSON schema at `/openapi.json`
    """,
    version="1.0.0",
    contact={"name": "Keniiy", "email": "kehindekehinde894@gmail.com"},
    lifespan=lifespan,
)


# Add CORS middleware
def get_cors_origins() -> List[str]:
    """
    Get CORS allowed origins based on environment.
    - Development: Allow all origins ("*")
    - Production: Use CORS_ORIGINS from settings (comma-separated list)
    """
    if settings.debug:
        return ["*"]  # Allow all in development

    # In production, use configured origins
    cors_origins = settings.cors_origins
    if cors_origins == "*":
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            "⚠️  CORS_ORIGINS is set to '*' in production. "
            "This is insecure! Set CORS_ORIGINS to specific domains."
        )
        return ["*"]
    if isinstance(cors_origins, str):
        return [cors_origins]
    return cors_origins  # Already a list


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - first added is outermost)
app.add_middleware(TraceIDMiddleware)  # Add trace IDs to all requests
app.add_middleware(RateLimitMiddleware)  # Apply global rate limiting to all endpoints

# Register exception handlers (order matters - most specific first)
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Attach rate limiter to app
app.state.limiter = limiter

# Include routers
app.include_router(auth_router)


@app.get("/health")
async def health():
    """Enhanced health check endpoint"""
    from sqlalchemy import text

    from app.infrastructure.cache.redis_client import redis_client
    from app.infrastructure.db.config import engine

    health_status = {"status": "ok", "service": "api", "version": "1.0.0"}

    # Check database connectivity
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["database_error"] = str(e) if settings.debug else "Database connection failed"
        health_status["status"] = "degraded"

    # Check Redis connectivity
    redis_ok, redis_msg = await redis_client.health_check()
    health_status["redis"] = "connected" if redis_ok else "disconnected"
    if not redis_ok and settings.debug:
        health_status["redis_error"] = redis_msg

    return health_status
