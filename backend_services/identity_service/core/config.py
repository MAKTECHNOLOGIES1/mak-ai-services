"""
Identity Service Configuration
Supports Supabase PostgreSQL, Cloudflare D1/Hyperdrive, and any Cloud Postgres
"""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env at service level, root monorepo, or current working directory
SERVICE_DIR = Path(__file__).resolve().parents[1]
MONOREPO_ROOT = Path(__file__).resolve().parents[3]

env_files = [
    MONOREPO_ROOT / ".env",
    SERVICE_DIR / ".env",
    Path.cwd() / ".env"
]
active_env_file = next((f for f in env_files if f.exists()), None)

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AMK Identity Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8001

    # Database: Supports Supabase URL directly or component credentials
    DATABASE_URL: str = Field(
        default="",
        description="Full connection string (e.g., Supabase postgresql+asyncpg://...)"
    )
    DB_HOST: str = "aws-0-ap-south-1.pooler.supabase.com"
    DB_PORT: int = 6543
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres.enkssiilvwiemxvsqaoy"
    DB_PASSWORD: str = "Anil_21kb1a3029"
    DB_SSL_MODE: str = "require" # 'require' for Supabase cloud
    DB_SCHEMA: str = "identity_service"

    # JWT Security
    JWT_SECRET: str = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    def get_database_url(self) -> str:
        """Returns the async connection string for SQLAlchemy with asyncpg and SSL"""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Ensure using asyncpg driver for asynchronous queries
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # Ensure SSL is specified for Supabase
            if "supabase.co" in url and "ssl=" not in url and "sslmode=" not in url:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}ssl=require"
            return url
        
        # Fallback to individual components with URL-encoded password
        encoded_password = quote_plus(self.DB_PASSWORD)
        ssl_arg = f"?ssl={self.DB_SSL_MODE}" if self.DB_SSL_MODE in ["require", "verify-full"] else ""
        return f"postgresql+asyncpg://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_arg}"

    model_config = SettingsConfigDict(
        env_file=active_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

