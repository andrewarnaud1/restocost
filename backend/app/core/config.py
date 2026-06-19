"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        PROJECT_NAME: Name of the project.
        VERSION: Application version.
        API_V1_PREFIX: API version 1 prefix.
        DATABASE_URL: PostgreSQL database connection URL.
        SECRET_KEY: Secret key for JWT tokens.
        ALGORITHM: JWT encoding algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes.
    """

    PROJECT_NAME: str = "RestoCost"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://restocost:restocost@localhost:5432/restocost"
    )

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: The application settings instance.
    """
    return Settings()
