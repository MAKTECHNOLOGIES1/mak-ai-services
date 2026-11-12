"""
FastAPI Dependencies: Authentication & Dynamic Role-Based Authorization
Using custom user_id, tenant_id, and role_id
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.database import get_db
from core.security import decode_access_token
from models.user_model import User
from models.role_model import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extracts, validates JWT and fetches current user by user_id"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub") # Student Roll Number or Staff ID
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been disabled"
        )

    return user

def require_roles(allowed_role_ids: List[str]):
    """Checks if current user's role_id is in allowed roles"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        allowed_upper = [r.upper() if r.upper().startswith("ROLE_") else f"ROLE_{r.upper()}" for r in allowed_role_ids]
        if current_user.role_id.upper() not in allowed_upper:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_role_ids}"
            )
        return current_user
    return role_checker

def require_min_hierarchy(min_level: int):
    """Allows any user whose role hierarchy level >= min_level"""
    async def hierarchy_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        result = await db.execute(select(Role).where(Role.role_id == current_user.role_id))
        role = result.scalar_one_or_none()
        current_level = role.hierarchy_level if role else 0

        if current_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privilege level ({current_level}). Minimum required is {min_level}."
            )
        return current_user
    return hierarchy_checker
