"""
AMK Technologies - API Gateway Application Entrypoint
Centralized Reverse Proxy, Pre-Authentication, Rate Limiting, and CORS.
Compatible with Cloudflare Python Workers (Pyodide ASGI).
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.middleware import (
    CorrelationIdMiddleware,
    RateLimitMiddleware,
    AuthPreValidationMiddleware
)
from routes.proxy_routes import router as proxy_router
from services.proxy_service import close_http_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("[Gateway] %s started on port %s (%s)", settings.APP_NAME, settings.PORT, settings.ENVIRONMENT)
    yield
    # Shutdown
    await close_http_client()


app = FastAPI(
    title=settings.APP_NAME,
    description="Centralized API Gateway & Reverse Proxy for AMK College Transformation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 1. Global CORS Middleware (Must be outer layer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "Content-Disposition"]
)

# 2. Add Gateway Middlewares (Executed in order)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(AuthPreValidationMiddleware)

# 3. Include Proxy Routing Table
app.include_router(proxy_router)


# 4. Gateway Health Check
@app.get("/health", tags=["Health"])
async def gateway_health():
    return {
        "service": "api_gateway",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "identity_service": settings.IDENTITY_SERVICE_URL,
        "tenant_service": settings.TENANT_SERVICE_URL
    }


# 5. Cloudflare Workers Python ASGI Handler
try:
    from workers import asgi
    Default = asgi.entrypoint(app)
except (ImportError, Exception):
    Default = app


async def on_fetch(request, env):
    try:
        import os
        # Sync Cloudflare Worker secrets into os.environ for Pydantic Settings
        if hasattr(env, "items"):
            for k, v in env.items():
                os.environ[str(k)] = str(v)
        elif hasattr(env, "__dict__"):
            for k, v in env.__dict__.items():
                if not str(k).startswith("_"):
                    os.environ[str(k)] = str(v)

        from workers import asgi
        return await asgi.fetch(app, request, env)
    except Exception:
        try:
            import asgi
            return await asgi.fetch(app, request, env)
        except Exception:
            return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
