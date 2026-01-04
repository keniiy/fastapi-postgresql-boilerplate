from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Optional, List, Union


class Settings(BaseSettings):
    # App
    environment: str = "development"
    debug: bool = True

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """Parse debug value, handling string inputs"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return True  # Default to True if invalid

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> Union[str, List[str]]:
        """
        Parse CORS origins from environment variable.
        Accepts:
        - Comma-separated string: "https://app1.com,https://app2.com"
        - JSON array string: '["https://app1.com","https://app2.com"]'
        - List (already parsed)
        """
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON array first
            if v.strip().startswith("["):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Otherwise treat as comma-separated
            if v.strip() == "*" or v.strip() == "":
                return "*"
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else "*"
        return "*"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/app_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Security
    secret_key: str = "dev-secret-key-change-in-production-min-32-characters-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: Union[str, List[str]] = "*"  # Comma-separated string or JSON array

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "1000/hour"  # Global default rate limit for all endpoints
    rate_limit_storage: str = "memory://"  # Use "redis://localhost:6379" in production

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_json_format: bool = False  # Use JSON structured logging (False for readable dev logs)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Ignore invalid environment variables, use defaults
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
