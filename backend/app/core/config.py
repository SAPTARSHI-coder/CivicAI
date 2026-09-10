"""Application settings loaded from the environment.

Plain FastAPI — no database, no secrets required. Everything has a sensible
default so the app boots with zero configuration. Override any field via the
environment or a ``.env`` file.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Project metadata -------------------------------------------------
    PROJECT_NAME: str = "CivicAI API"
    DESCRIPTION: str = "CivicAI: Your AI Public Service Officer API."
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # --- Runtime ----------------------------------------------------------
    ENVIRONMENT: Literal["local", "test", "staging", "production"] = "local"
    DEBUG: bool = False
    ENABLE_DOCS: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # --- CORS (comma-separated origins) -----------------------------------
    BACKEND_CORS_ORIGINS: str = ""

    # --- AI Providers -----------------------------------------------------
    GEMINI_API_KEY: str = ""

    @property
    def gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY.strip())

    # --- Cloudinary (original document storage) ---------------------------
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    @property
    def cloudinary_configured(self) -> bool:
        return bool(
            self.CLOUDINARY_CLOUD_NAME.strip()
            and self.CLOUDINARY_API_KEY.strip()
            and self.CLOUDINARY_API_SECRET.strip()
        )

    # --- Snowflake Settings (persistent analytics/session logging) --------
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_WAREHOUSE: str = ""
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_SCHEMA: str = ""
    SNOWFLAKE_ROLE: str = ""

    @property
    def snowflake_configured(self) -> bool:
        return bool(
            self.SNOWFLAKE_ACCOUNT.strip()
            and self.SNOWFLAKE_USER.strip()
            and self.SNOWFLAKE_PASSWORD.strip()
            and self.SNOWFLAKE_WAREHOUSE.strip()
            and self.SNOWFLAKE_DATABASE.strip()
            and self.SNOWFLAKE_SCHEMA.strip()
        )

    @property
    def cors_origins(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()


settings = get_settings()
