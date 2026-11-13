"""
AMK Technologies - API Gateway Application Entrypoint
Centralized Reverse Proxy, Pre-Authentication, Rate Limiting, and CORS
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.middleware import (
    CorrelationIdMiddleware,
    RateLimitMiddleware,
    AuthPreValidationMiddleware
)
from routes.proxy_routes import router as proxy_router
from services.proxy_service import http_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[Gateway] {settings.APP_NAME} started on port {settings.PORT} ({settings.ENVIRONMENT})")
    print(f"[Gateway] Routing auth to {settings.IDENTITY_SERVICE_URL}")
    yield
    # Shutdown: Close HTTP connection pool
    await http_client.aclose()
    print(f"[Gateway] Cleaned up HTTP client pool.")

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
