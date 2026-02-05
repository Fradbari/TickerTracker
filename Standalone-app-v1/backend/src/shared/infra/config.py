"""
Configuration management for TickerTracker application.

Uses pydantic-settings for multi-environment configuration with support for:
- Environment-specific variables (local, staging, production)
- Secret management (SecretStr for sensitive values)
- .env file loading with fallback defaults
- Singleton pattern with caching via functools.lru_cache
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with multi-environment support.

    Configuration priority (highest to lowest):
    1. Environment variables
    2. .env file
    3. Default values defined here
    """

    # ========== Environment Configuration ==========
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(
        default="local",
        description="Application environment",
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode (should be False in production)",
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for application",
    )

    # ========== Database Configuration ==========
    DATABASE_URL: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev"),
        description="Database connection URL (use PostgreSQL in production)",
    )

    # ========== External API Configuration ==========
    YAHOO_CACHE_TTL: int = Field(
        default=3600,
        description="Cache TTL in seconds for Yahoo Finance data (1 hour default)",
    )
    GEMINI_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Google Gemini API key for AI features (required in production)",
    )
    FINNHUB_API_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Finnhub API key for market data (optional)",
    )

    # ========== Google Drive Configuration ==========
    GOOGLE_SERVICE_ACCOUNT_JSON: SecretStr = Field(
        default=SecretStr(""),
        description="Google Service Account JSON key for Drive access (as JSON string)",
    )
    DRIVE_FOLDER_ID: str = Field(
        default="",
        description="Google Drive folder ID for data storage",
    )

    # ========== Security Configuration ==========
    ENCRYPTION_KEY: SecretStr = Field(
        default=SecretStr(""),
        description="Encryption key for sensitive data (generate with: openssl rand -hex 32)",
    )
    JWT_SECRET: SecretStr = Field(
        default=SecretStr(""),
        description="JWT secret key for authentication tokens",
    )

    # ========== Middleware Configuration ==========
    ENABLE_RATE_LIMIT: bool = Field(
        default=True,
        description="Enable rate limiting middleware (disable for local development)",
    )
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit: max requests per minute per IP",
    )
    CORS_ORIGINS: list[str] = Field(
        default=[],
        description="Additional CORS origins (comma-separated or list in env)",
    )

    # ========== Pydantic Configuration ==========
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Ignore extra environment variables
        extra="ignore",
        # Validate default values
        validate_default=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses functools.lru_cache to ensure only one Settings instance exists,
    reducing I/O operations and environment variable parsing overhead.

    Returns:
        Settings: Singleton Settings instance

    Example:
        >>> settings = get_settings()
        >>> print(settings.ENVIRONMENT)
        'local'
        >>> print(settings.DEBUG)
        True
    """
    return Settings()
