"""
AMK Identity Service Application Entrypoint
Handles authentication, dynamic roles, and user provisioning.
Lightweight — uses Supabase PostgREST (no SQLAlchemy) for Cloudflare Workers compatibility.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import get_db_client
from routes.auth_routes import router as auth_router
from routes.role_routes import router as role_router
from routes.user_routes import router as user_router
from services.role_service import RoleService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed default roles in Supabase if not present
    try:
        db = get_db_client()
        if db:
            await RoleService.seed_default_roles_if_missing(db)
    except Exception as e:
        logger.warning("Could not seed roles on startup (DB connection may not be active yet): %s", e)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant authentication and dynamic role provisioning engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration for Gateway, Frontend and Cloudflare environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mak-ui-test.anilkumarreddy3029.workers.dev",
        "https://mak-ui.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway-test.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway.anilkumarreddy3029.workers.dev",
        "https://*.workers.dev",
        "https://*.amktech.in",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under standard /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "service": "identity_service",
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
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
