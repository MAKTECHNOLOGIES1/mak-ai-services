"""
User Management API Endpoints
All IDs are clean custom strings
"""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_user, require_min_hierarchy
from models.user_model import User
from schemas.auth_schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get(
    "",
    response_model=List[UserResponse],
    summary="List Users in Tenant",
    description="Returns users in current college. Filterable by role_id (e.g. ROLE_FACULTY), department, etc."
)
async def list_tenant_users(
    role_id: Optional[str] = Query(None, description="Filter by role_id (e.g. ROLE_STUDENT, ROLE_FACULTY)"),
    department: Optional[str] = Query(None, description="Filter by department (e.g. CSE)"),
    current_user: User = Depends(require_min_hierarchy(min_level=50)), # Faculty / TPO / HOD / Admin
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.tenant_id == current_user.tenant_id)
    if role_id:
        query = query.where(User.role_id == role_id.upper())
    if department:
        query = query.where(User.department == department.upper())

    result = await db.execute(query.order_by(User.created_at.desc()))
    users = list(result.scalars().all())

    response_list = []
    for u in users:
        r = UserResponse.model_validate(u)
        if u.role:
            r.role_name = u.role.name
        response_list.append(r)

    return response_list

@router.patch(
    "/{target_user_id}/status",
    response_model=UserResponse,
    summary="Activate / Deactivate User Account"
)
async def toggle_user_status(
    target_user_id: str, # Student Roll Number or Staff ID (e.g. "22731A0501" or "FAC-SRIT-001")
    is_active: bool,
    current_user: User = Depends(require_min_hierarchy(min_level=80)), # Manager / Admin
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            User.tenant_id == current_user.tenant_id,
            User.user_id == target_user_id.upper()
        )
    )
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{target_user_id}' not found")

    target_user.is_active = is_active
    await db.commit()
    await db.refresh(target_user)

    resp = UserResponse.model_validate(target_user)
    if target_user.role:
        resp.role_name = target_user.role.name
    return resp
