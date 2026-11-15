"""
Advanced Authentication & Authorization Dependencies for Tenant Service
- Validates JWT from API Gateway or Direct Request
- Enforces Role-Based Access Control (RBAC) & Hierarchy
- Multi-Tenant Isolation: Prevents tenant A from accessing tenant B data
- Microservice-to-Microservice Service Key verification (identity_service integration)
"""

from typing import Any, Optional
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token, verify_internal_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user_claims(
    token: Optional[str] = Depends(oauth2_scheme)
) -> dict[str, Any]:
    """
    Extracts and validates JWT claims from Bearer token.
    Returns: dict with user_id, tenant_id, role_id, permissions
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    claims = decode_access_token(token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Standard claims mapping from identity_service
    user_id = claims.get("sub") or claims.get("user_id")
    tenant_id = claims.get("tenant_id")
    role_id = claims.get("role_id", "ROLE_STUDENT")
    permissions = claims.get("permissions", [])

    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing required identity claims (user_id/tenant_id)"
        )

    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role_id": role_id.upper(),
        "permissions": permissions
    }

def require_roles(allowed_role_ids: list[str]):
    """
    Dependency factory to check if the user belongs to one of allowed roles.
    Accepts roles with or without 'ROLE_' prefix (e.g. ['ADMIN', 'SUPERADMIN']).
    """
    normalized_allowed = [
        r.upper() if r.upper().startswith("ROLE_") else f"ROLE_{r.upper()}"
        for r in allowed_role_ids
    ]

    async def role_checker(claims: dict[str, Any] = Depends(get_current_user_claims)) -> dict[str, Any]:
        user_role = claims["role_id"].upper()
        if user_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_role_ids}"
            )
        return claims

    return role_checker

async def verify_tenant_isolation(
    tenant_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims)
) -> dict[str, Any]:
    """
    Ensures a college admin or staff can only query/modify their own tenant.
    ROLE_SUPERADMIN is exempted and can access all tenants.
    """
    user_role = claims["role_id"].upper()
    if user_role in ["ROLE_SUPERADMIN", "ROLE_SYSTEM"]:
        return claims

    if claims["tenant_id"].upper() != tenant_id.upper():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant Isolation Violation: You are not authorized to access tenant '{tenant_id}'."
        )

    return claims

async def verify_service_or_admin(
    x_service_key: Optional[str] = Header(None, alias="X-Internal-Service-Key"),
    token: Optional[str] = Depends(oauth2_scheme)
) -> dict[str, Any]:
    """
    Allows either an internal microservice key (e.g. from identity_service)
    OR a valid admin/superadmin JWT bearer token.
    """
    # 1. Try internal service key
    if x_service_key and verify_internal_key(x_service_key):
        return {"caller": "internal_service", "role_id": "ROLE_INTERNAL"}

    # 2. Try bearer token
    if token:
        claims = decode_access_token(token)
        if claims:
            user_role = (claims.get("role_id") or "").upper()
            if user_role in ["ROLE_SUPERADMIN", "ROLE_ADMIN", "ROLE_SYSTEM"]:
                return claims

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized caller. Valid X-Internal-Service-Key or Admin JWT required."
    )

