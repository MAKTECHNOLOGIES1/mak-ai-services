"""
Identity Service Configuration
All configuration and secrets are strictly loaded from environment variables (.env / Cloudflare Worker Secrets).
No hardcoded keys, database URLs, or secrets.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

active_env_file = None
try:
    SERVICE_DIR = Path(__file__).resolve().parents[1]
    MONOREPO_ROOT = Path(__file__).resolve().parents[3]
    env_files = [
        SERVICE_DIR / ".env",
        MONOREPO_ROOT / ".env",
        Path.cwd() / ".env"
    ]
    active_env_file = next((f for f in env_files if f.is_file()), None)
except Exception:
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=active_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Service Metadata
    APP_NAME: str = Field(default="AMK Identity Service")
    SERVICE_NAME: str = Field(default="identity_service")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    PORT: int = Field(default=8001)

    # Supabase PostgREST Credentials (Loaded from .env / Cloudflare Secrets)
    SUPABASE_URL: str = Field(default="")
    SUPABASE_SERVICE_KEY: str = Field(default="")
    DB_SCHEMA: str = Field(default="identity_service")

    # JWT Authentication Secrets (Loaded from .env / Cloudflare Secrets)
    JWT_SECRET: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)

    # Inter-Service Security (Loaded from .env / Cloudflare Secrets)
    INTERNAL_SERVICE_KEY: str = Field(default="")

    # Tenant Fallback
    DEFAULT_TENANT_ID: Optional[str] = Field(default=None)


settings = Settings()
