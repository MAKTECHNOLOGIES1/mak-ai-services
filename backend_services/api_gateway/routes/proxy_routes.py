"""
API Gateway Proxy Routing Table
Maps frontend URI paths to downstream microservices
"""

from fastapi import APIRouter, Request, Response
from core.config import settings
from services.proxy_service import proxy_to_service

router = APIRouter()

# -------------------------------------------------------------
# 1. Identity Service Routes (Auth, Roles, Users)
# -------------------------------------------------------------
@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_auth(request: Request, path: str):
    return await proxy_to_service(request, settings.IDENTITY_SERVICE_URL, f"api/v1/auth/{path}")

@router.api_route("/api/v1/roles/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_roles(request: Request, path: str):
    return await proxy_to_service(request, settings.IDENTITY_SERVICE_URL, f"api/v1/roles/{path}")

@router.api_route("/api/v1/roles", methods=["GET", "POST"])
async def route_roles_root(request: Request):
    return await proxy_to_service(request, settings.IDENTITY_SERVICE_URL, "api/v1/roles")

@router.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_users(request: Request, path: str):
    return await proxy_to_service(request, settings.IDENTITY_SERVICE_URL, f"api/v1/users/{path}")

# -------------------------------------------------------------
# 2. Tenant Service Routes (Colleges, Modules, Quotas)
# -------------------------------------------------------------
@router.api_route("/api/v1/tenants/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_tenants(request: Request, path: str):
    return await proxy_to_service(request, settings.TENANT_SERVICE_URL, f"api/v1/tenants/{path}")

@router.api_route("/api/v1/tenants", methods=["GET", "POST"])
async def route_tenants_root(request: Request):
    return await proxy_to_service(request, settings.TENANT_SERVICE_URL, "api/v1/tenants")

# -------------------------------------------------------------
# 3. Knowledge Base & Academic Regulations RAG Service Routes
# -------------------------------------------------------------
@router.api_route("/api/v1/knowledge/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_knowledge(request: Request, path: str):
    return await proxy_to_service(request, settings.KNOWLEDGE_RAG_SERVICE_URL, f"api/v1/knowledge/{path}")

# -------------------------------------------------------------
# 4. AI Gateway & Model Routing Service Routes
# -------------------------------------------------------------
@router.api_route("/api/v1/ai-gateway/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_ai_gateway(request: Request, path: str):
    return await proxy_to_service(request, settings.AI_GATEWAY_SERVICE_URL, f"api/v1/ai-gateway/{path}")

# -------------------------------------------------------------
# 5. Faculty AI Generation Service Routes
# -------------------------------------------------------------
@router.api_route("/api/v1/faculty-ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_faculty_ai(request: Request, path: str):
    return await proxy_to_service(request, settings.FACULTY_AI_SERVICE_URL, f"api/v1/faculty-ai/{path}")

# -------------------------------------------------------------
# 6. Project Studio Capstone Service Routes
# -------------------------------------------------------------
@router.api_route("/api/v1/projects/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_projects(request: Request, path: str):
    return await proxy_to_service(request, settings.PROJECT_STUDIO_SERVICE_URL, f"api/v1/projects/{path}")

# -------------------------------------------------------------
# 7. Learning Hub & Courses Service Routes
# -------------------------------------------------------------
@router.api_route("/api/v1/learning/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_learning(request: Request, path: str):
    return await proxy_to_service(request, settings.LEARNING_SERVICE_URL, f"api/v1/learning/{path}")

# -------------------------------------------------------------
# Gateway Service Directory & Status
# -------------------------------------------------------------
@router.get("/api/v1/gateway/routes", tags=["Gateway Registry"])
async def get_gateway_routes():
    """Returns the routing directory and active destinations"""
    return {
        "gateway": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "routes": {
            "/api/v1/auth/*": settings.IDENTITY_SERVICE_URL,
            "/api/v1/roles/*": settings.IDENTITY_SERVICE_URL,
            "/api/v1/users/*": settings.IDENTITY_SERVICE_URL,
            "/api/v1/tenants/*": settings.TENANT_SERVICE_URL,
            "/api/v1/knowledge/*": settings.KNOWLEDGE_RAG_SERVICE_URL,
            "/api/v1/ai-gateway/*": settings.AI_GATEWAY_SERVICE_URL,
            "/api/v1/faculty-ai/*": settings.FACULTY_AI_SERVICE_URL,
            "/api/v1/projects/*": settings.PROJECT_STUDIO_SERVICE_URL,
            "/api/v1/learning/*": settings.LEARNING_SERVICE_URL
        }
    }

