"""
Tenant Service Configuration
Supports Supabase PostgreSQL poolers, Cloudflare Workers, and multi-tenant JWT validation
"""

from pathlib import Path
from urllib.parse import quote_plus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[1]
MONOREPO_ROOT = Path(__file__).resolve().parents[3]

env_files = [
    MONOREPO_ROOT / ".env",
    SERVICE_DIR / ".env",
    Path.cwd() / ".env"
]
active_env_file = next((f for f in env_files if f.exists()), None)

class Settings(BaseSettings):
    APP_NAME: str = "AMK Tenant Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8002

    # Database Configuration (Supabase PostgreSQL)
    DATABASE_URL: str = Field(
        default="",
        description="Full connection string (e.g. Supabase postgresql+asyncpg://...)"
    )
    DB_HOST: str = "aws-0-ap-south-1.pooler.supabase.com"
    DB_PORT: int = 6543
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres.enkssiilvwiemxvsqaoy"
    DB_PASSWORD: str = "Anil_21kb1a3029"
    DB_SSL_MODE: str = "require"
    DB_SCHEMA: str = "identity_service"

    # JWT Authentication
    JWT_SECRET: str = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    JWT_ALGORITHM: str = "HS256"

    # Microservice-to-Microservice Internal Security
    INTERNAL_SERVICE_KEY: str = "amk-internal-service-secret-key-2026"
    DEFAULT_TENANT_ID: str = "SRIT-ATP"

    def get_database_url(self) -> str:
        """Returns asyncpg connection string with SSL configuration"""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            if "supabase.co" in url and "ssl=" not in url and "sslmode=" not in url:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}ssl=require"
            return url

        encoded_password = quote_plus(self.DB_PASSWORD)
        ssl_arg = f"?ssl={self.DB_SSL_MODE}" if self.DB_SSL_MODE in ["require", "verify-full"] else ""
        return f"postgresql+asyncpg://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_arg}"

    model_config = SettingsConfigDict(
        env_file=active_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

