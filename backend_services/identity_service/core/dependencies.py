"""
FastAPI Authentication & Authorization Dependencies for Identity Service
Cloudflare Workers compatible, PostgREST / Supabase based
"""

from typing import Any, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.database import SupabaseClient, get_db
from core.security import decode_access_token, verify_internal_key
from models.role_model import role_from_row
from models.user_model import user_from_row

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Optional[SupabaseClient] = Depends(get_db)
) -> dict[str, Any]:
    """Extracts, validates JWT and fetches current user by user_id from Supabase"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db:
        # Fallback to claims-based user if DB client is temporarily unavailable
        return {
            "user_id": user_id,
            "tenant_id": payload.get("tenant_id"),
            "role_id": payload.get("role_id") or payload.get("role", "ROLE_STUDENT"),
            "full_name": payload.get("full_name", ""),
            "email": payload.get("email", ""),
            "department": payload.get("department", "GENERAL"),
            "is_active": True,
        }

    row = await db.select("users", filters={"user_id": f"eq.{user_id}"}, single=True)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been removed",
        )

    user = user_from_row(row)
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been disabled",
        )

    return user


def require_roles(allowed_role_ids: list[str]):
    """Checks if current user's role_id matches one of allowed roles"""
    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user)
    ) -> dict[str, Any]:
        allowed_normalized = [
            r.upper() if r.upper().startswith("ROLE_") else f"ROLE_{r.upper()}"
            for r in allowed_role_ids
        ]
        user_role = str(current_user.get("role_id", "")).upper()
        if user_role not in allowed_normalized and "ROLE_SUPER_ADMIN" not in user_role and "ROLE_SUPERADMIN" not in user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_role_ids}",
            )
        return current_user
    return role_checker


def require_min_hierarchy(min_level: int):
    """Allows any user whose role hierarchy level >= min_level"""
    async def hierarchy_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
        db: Optional[SupabaseClient] = Depends(get_db)
    ) -> dict[str, Any]:
        user_role_id = current_user.get("role_id", "ROLE_STUDENT")

        # Fast path for super admins
        if user_role_id in ["ROLE_SUPER_ADMIN", "ROLE_SUPERADMIN"]:
            return current_user

        level = 10
        if db:
            role_row = await db.select("roles", filters={"role_id": f"eq.{user_role_id}"}, single=True)
            if role_row:
                role = role_from_row(role_row)
                level = role.get("hierarchy_level", 10)

        if level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privilege level ({level}). Minimum required is {min_level}.",
            )
        return current_user
    return hierarchy_checker


async def verify_service_or_admin(
    x_internal_service_key: Optional[str] = Header(None, alias="X-Internal-Service-Key"),
    token: Optional[str] = Depends(oauth2_scheme)
) -> dict[str, Any]:
    """Allows internal inter-service calls or superadmin users"""
    if x_internal_service_key and verify_internal_key(x_internal_service_key):
        return {"source": "internal_service", "authorized": True}

    if token:
        claims = decode_access_token(token)
        if claims:
            role = str(claims.get("role") or claims.get("role_id", "")).upper()
            if role in ["ROLE_SUPERADMIN", "ROLE_SUPER_ADMIN", "ROLE_ADMIN"]:
                return {"source": "admin_jwt", "claims": claims}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid X-Internal-Service-Key or Admin Bearer token required.",
    )
