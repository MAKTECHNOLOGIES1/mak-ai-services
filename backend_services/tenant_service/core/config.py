"""
Tenant Service Configuration
Supports Supabase PostgREST, Cloudflare Workers, and multi-tenant JWT validation
"""

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

active_env_file = None
try:
    SERVICE_DIR = Path(__file__).resolve().parents[1]
    MONOREPO_ROOT = Path(__file__).resolve().parents[3]
    env_files = [
        MONOREPO_ROOT / ".env",
        SERVICE_DIR / ".env",
        Path.cwd() / ".env"
    ]
    active_env_file = next((f for f in env_files if f.is_file()), None)
except Exception:
    pass

class Settings(BaseSettings):
    APP_NAME: str = "AMK Tenant Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8002

    # Supabase Configuration (PostgREST / REST API)
    SUPABASE_URL: str = Field(
        default="",
        description="Supabase project URL (e.g. https://enkssiilvwiemxvsqaoy.supabase.co)"
    )
    SUPABASE_SERVICE_KEY: str = Field(
        default="",
        description="Supabase service_role key for server-side access"
    )
    DB_SCHEMA: str = "identity_service"

    # Legacy DB fields
    DATABASE_URL: str = ""
    DB_HOST: str = "aws-0-ap-south-1.pooler.supabase.com"
    DB_PORT: int = 6543
    DB_NAME: str = "postgres"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_SSL_MODE: str = "require"

    # JWT Authentication
    JWT_SECRET: str = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    JWT_ALGORITHM: str = "HS256"

    # Microservice-to-Microservice Internal Security
    INTERNAL_SERVICE_KEY: str = "amk-internal-service-secret-key-2026"
    DEFAULT_TENANT_ID: str = "SRIT-ATP"

    model_config = SettingsConfigDict(
        env_file=active_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
