"""
AMK Tenant Service Application Entrypoint
Handles college onboarding, seat cap validations, and module feature toggles
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import AsyncSessionLocal
from routes.internal_routes import router as internal_router
from routes.tenant_routes import router as tenant_router
from services.tenant_service import TenantService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure default tenant exists in Supabase
    try:
        if AsyncSessionLocal is not None:
            async with AsyncSessionLocal() as session:
                await TenantService.seed_default_tenant_if_missing(session)
    except Exception as e:
        logger.warning("Could not check/seed default tenant on startup: %s", e)
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant college onboarding and hard seat cap governance service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration for Gateway and Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mak-ui-test.anilkumarreddy3029.workers.dev",
        "https://mak-ui.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway-test.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway.anilkumarreddy3029.workers.dev",
        "https://*.workers.dev",
        "https://*.amktech.in",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register Routers under /api/v1 prefix
app.include_router(tenant_router, prefix="/api/v1")
app.include_router(internal_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "service": "tenant_service",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# Cloudflare Workers Python ASGI Handler
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
