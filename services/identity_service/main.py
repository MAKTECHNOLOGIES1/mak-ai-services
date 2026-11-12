"""
AMK Identity Service Application Entrypoint
Handles authentication, dynamic roles, and user provisioning
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import AsyncSessionLocal
from services.role_service import RoleService
from routes.auth_routes import router as auth_router
from routes.role_routes import router as role_router
from routes.user_routes import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed default roles in PostgreSQL / Supabase if not present
    try:
        async with AsyncSessionLocal() as session:
            await RoleService.seed_default_roles_if_missing(session)
    except Exception as e:
        print(f"[Warning] Could not seed roles on startup (DB connection may not be active yet): {e}")
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant authentication and dynamic role provisioning engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.amktech.in",
        "*"
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
        "environment": settings.ENVIRONMENT
    }

# Cloudflare Workers Python ASGI Handler
async def on_fetch(request, env):
    try:
        import asgi
        return await asgi.fetch(app, request, env)
    except ImportError:
        # Standard ASGI fallback
        return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
