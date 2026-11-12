"""
API Gateway Configuration
Dynamically routes to Cloudflare Workers environments (Test & Production)
ZERO localhost URLs - All routing uses Cloudflare Workers URLs
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

SERVICE_DIR = Path(__file__).resolve().parents[1]
MONOREPO_ROOT = Path(__file__).resolve().parents[3]

env_files = [
    MONOREPO_ROOT / ".env",
    SERVICE_DIR / ".env",
    Path.cwd() / ".env"
]
active_env_file = next((f for f in env_files if f.exists()), None)

class GatewaySettings(BaseSettings):
    APP_NAME: str = "AMK API Gateway"
    ENVIRONMENT: str = "test" # 'test' or 'production'
    DEBUG: bool = True
    PORT: int = 8000

    # JWT Authentication
    JWT_SECRET: str = "404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970"
    JWT_ALGORITHM: str = "HS256"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Cloudflare Workers Account Domain
    CF_WORKERS_DOMAIN: str = "anilkumarreddy3029.workers.dev"

    def get_service_url(self, service_slug: str) -> str:
        """
        Dynamically constructs Cloudflare Workers URL based on ENVIRONMENT:
        - In 'test': https://mak-{service_slug}-test.anilkumarreddy3029.workers.dev
        - In 'production': https://mak-{service_slug}.anilkumarreddy3029.workers.dev
        """
        slug = service_slug.replace("_", "-")
        if self.ENVIRONMENT == "production":
            return f"https://mak-{slug}.{self.CF_WORKERS_DOMAIN}"
        else:
            return f"https://mak-{slug}-test.{self.CF_WORKERS_DOMAIN}"

    @property
    def IDENTITY_SERVICE_URL(self) -> str:
        return os.getenv("IDENTITY_SERVICE_URL") or self.get_service_url("identity-service")

    @property
    def TENANT_SERVICE_URL(self) -> str:
        return os.getenv("TENANT_SERVICE_URL") or self.get_service_url("tenant-service")

    @property
    def AI_GATEWAY_SERVICE_URL(self) -> str:
        return os.getenv("AI_GATEWAY_SERVICE_URL") or self.get_service_url("ai-gateway-service")

    @property
    def KNOWLEDGE_RAG_SERVICE_URL(self) -> str:
        return os.getenv("KNOWLEDGE_RAG_SERVICE_URL") or self.get_service_url("knowledge-rag-service")

    @property
    def FACULTY_AI_SERVICE_URL(self) -> str:
        return os.getenv("FACULTY_AI_SERVICE_URL") or self.get_service_url("faculty-ai-service")

    @property
    def PROJECT_STUDIO_SERVICE_URL(self) -> str:
        return os.getenv("PROJECT_STUDIO_SERVICE_URL") or self.get_service_url("project-studio-service")

    @property
    def LEARNING_SERVICE_URL(self) -> str:
        return os.getenv("LEARNING_SERVICE_URL") or self.get_service_url("learning-service")

    # Cloudflare CORS Allowed Origins (NO localhost)
    CORS_ORIGINS: List[str] = [
        "https://mak-ui-test.anilkumarreddy3029.workers.dev",
        "https://mak-ui.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway-test.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway.anilkumarreddy3029.workers.dev",
        "https://*.workers.dev",
        "https://*.amktech.in",
        "*"
    ]

    # Public Unauthenticated Paths
    PUBLIC_PATHS: List[str] = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/register/student",
        "/api/v1/roles"
    ]

    model_config = SettingsConfigDict(
        env_file=active_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = GatewaySettings()
