"""
config.py - Application settings loaded from environment / .env file.

Uses pydantic-settings for type-safe, validated configuration.
A single `settings` singleton is imported across the application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/flagship_db"

    # -------------------------------------------------------------------------
    # AI
    # -------------------------------------------------------------------------
    GEMINI_API_KEY: str = ""

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    APP_NAME: str = "AI Restaurant Feedback Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False


# Module-level singleton — import this everywhere.
settings = Settings()
