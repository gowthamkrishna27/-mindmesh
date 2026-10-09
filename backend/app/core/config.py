"""Application configuration using Pydantic Settings.

Secrets are loaded only from environment variables.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.settings_rules import (
    DEFAULT_MIN_QUESTIONS_PER_CONCEPT,
    DEFAULT_MIN_RETEST_ITEMS_PER_CONCEPT,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "MindMesh"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False

    # Database Configuration (supports SQLite for local testing, PostgreSQL in production)
    DATABASE_URL: str = "sqlite:///./mindmesh.db"

    # Security: Secrets only in environment variables
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-never-commit-actual-secrets"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Content thresholds
    MIN_QUESTIONS_PER_CONCEPT: int = DEFAULT_MIN_QUESTIONS_PER_CONCEPT
    MIN_RETEST_ITEMS_PER_CONCEPT: int = DEFAULT_MIN_RETEST_ITEMS_PER_CONCEPT

    # LLM configuration (disabled by default)
    LLM_ENABLED: bool = False
    LLM_PROVIDER: str = "none"
    LLM_API_KEY: str = ""


settings = Settings()
