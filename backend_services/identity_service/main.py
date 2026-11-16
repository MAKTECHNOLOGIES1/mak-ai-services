"""
AMK Identity Service Application Entrypoint
Handles authentication, direct student onboarding (no tenant assigned), 
college staff provisioning, and inter-service token verification.
Compatible with Cloudflare Python Workers (Pyodide ASGI) and local Uvicorn development.
"""

import logging
import os
from typing import Any
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
        "environment": os.getenv("ENVIRONMENT") or settings.ENVIRONMENT
    }


# ── Cloudflare Workers Python ASGI Handler & Secret Sync ─────────────────────
_worker_env: Any = None


def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from os.environ, Worker env, or fallback."""
    val = os.getenv(key)
    if val:
        return val
    global _worker_env
    if _worker_env is not None:
        try:
            v = getattr(_worker_env, key, None)
            if v is not None:
                return str(v)
        except Exception:
            pass
        try:
            v = _worker_env[key]
            if v is not None:
                return str(v)
        except Exception:
            pass
    return default


try:
    from workers import asgi
    Default = asgi.entrypoint(app)
except (ImportError, Exception):
    Default = app


async def on_fetch(request, env):
    global _worker_env
    _worker_env = env

    try:
        # 1. Sync via Pyodide JS Object.entries (Cloudflare Workers runtime)
        try:
            from js import Object as JsObject
            for entry in JsObject.entries(env):
                k = str(entry[0])
                v = str(entry[1])
                os.environ[k] = v
        except Exception:
            pass

        # 2. Sync via dir(env) for JsProxy attributes
        try:
            for k in dir(env):
                if not k.startswith("_"):
                    try:
                        v = getattr(env, k)
                        if isinstance(v, (str, int, float, bool)):
                            os.environ[k] = str(v)
                    except Exception:
                        pass
        except Exception:
            pass

        # 3. Standard dict .items() fallback
        if hasattr(env, "items"):
            for k, v in env.items():
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
