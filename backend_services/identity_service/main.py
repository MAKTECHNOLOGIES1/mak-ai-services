"""
AMK Identity Service Application Entrypoint
Handles authentication, direct student onboarding (no tenant assigned), 
college staff provisioning, and inter-service token verification.
Compatible with Cloudflare Python Workers (Pyodide ASGI) and local Uvicorn development.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routes.auth_routes import router as auth_router
from routes.internal_routes import router as internal_router
from routes.user_routes import router as user_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant Identity, Authentication, and RBAC Service for AMK Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for UI and API Gateway
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mak-ui-test.anilkumarreddy3029.workers.dev",
        "https://mak-ui.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway-test.anilkumarreddy3029.workers.dev",
        "https://mak-api-gateway.anilkumarreddy3029.workers.dev",
        "https://*.workers.dev",
        "https://*.amktech.in",
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register Routers under /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(internal_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "service": settings.SERVICE_NAME,
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# ── Cloudflare Workers Python ASGI Handler ───────────────────────────────────
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

