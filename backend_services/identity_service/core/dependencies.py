"""
FastAPI Dependencies for Identity Service
Provides JWT authentication, Role-Based Access Control, and inter-service security checks.
"""

import os
from typing import Any, Callable, List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from core.config import settings
from core.database import supabase
from core.security import decode_token

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> dict[str, Any]:
    """
    Extracts and validates the Bearer JWT token from the Authorization header.
    Returns the authenticated user's dictionary.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database to verify active status
    user = await supabase.select(
        table="users",
        filters={"user_id": f"eq.{user_id}"},
        single=True
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory to enforce Role-Based Access Control.
    Example: Depends(require_roles(["ROLE_ADMIN", "ROLE_SUPER_ADMIN"]))
    """
    async def _role_checker(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        user_role = current_user.get("role_id")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}, your role is: {user_role}",
            )
        return current_user

    return _role_checker


async def verify_internal_key(
    x_internal_service_key: Optional[str] = Header(None, alias="X-Internal-Service-Key")
) -> bool:
    """
    Verifies inter-service authentication secret key.
    Used by API Gateway and peer microservices for internal queries.
    """
    key = os.getenv("INTERNAL_SERVICE_KEY") or settings.INTERNAL_SERVICE_KEY
    if not key:
        # If no key configured in dev, permit
        return True

    if not x_internal_service_key or x_internal_service_key != key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing X-Internal-Service-Key",
        )
    return True

