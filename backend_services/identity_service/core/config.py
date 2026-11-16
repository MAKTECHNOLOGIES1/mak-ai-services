"""
Identity Service Configuration
Supports Supabase PostgREST, Cloudflare Workers, and multi-tenant JWT validation.
Loads from local .env and runtime Cloudflare Worker Secrets with project fallbacks.
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
    APP_NAME: str = "AMK Identity Service"
    SERVICE_NAME: str = "identity_service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8001

    # Supabase PostgREST Credentials
    SUPABASE_URL: str = Field(default="https://enkssiilvwiemxvsqaoy.supabase.co")
    SUPABASE_SERVICE_KEY: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVua3NzaWlsdndpZW14dnNxYW95Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5NDQ1NjIzNywiZXhwIjoyMTEwMDMyMjM3fQ.eimR4EzksdaREG5_zqE8_3acbbWZyjpH4p-lQIL1QG8"
    )
    DB_SCHEMA: str = "identity_service"

    # JWT Authentication Secrets
    JWT_SECRET: str = Field(
        default="404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Inter-Service Security
    INTERNAL_SERVICE_KEY: str = Field(
        default="amk-internal-service-secret-key-2026"
    )

    # Tenant Fallback
    DEFAULT_TENANT_ID: Optional[str] = "SRIT-ATP"


settings = Settings()
