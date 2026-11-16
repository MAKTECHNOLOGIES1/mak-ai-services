"""
User Management Routes for Identity Service
Endpoints for college admins, department heads, and users:
- POST /api/v1/users/provision (Admin provisioning)
- GET  /api/v1/users (List users)
- GET  /api/v1/users/{user_id} (Fetch user profile)
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user, require_roles
from models.role_model import SystemRole
from schemas.user_schemas import ProvisionUserRequest, UserResponse
from services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/provision",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision Staff or Faculty Account",
    description="Allows College Admins or HODs to provision official faculty, staff, or trainer accounts within seat limits."
)
async def provision_user(
    req: ProvisionUserRequest,
    admin_user: dict[str, Any] = Depends(require_roles([
        SystemRole.ROLE_SUPER_ADMIN,
        SystemRole.ROLE_ADMIN,
        SystemRole.ROLE_HOD,
        SystemRole.ROLE_TECHNICAL_MANAGER
    ]))
):
    return await user_service.provision_user(admin_user, req)


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List Users",
    description="List users with optional filters by role, department, or tenant."
)
async def list_users(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict[str, Any] = Depends(get_current_user)
):
    # Non-super-admins can only view users in their own tenant (or general students if permitted)
    if current_user.get("role_id") != SystemRole.ROLE_SUPER_ADMIN:
        user_tenant = current_user.get("tenant_id")
        if user_tenant:
            tenant_id = user_tenant

    return await user_service.list_users(
        tenant_id=tenant_id,
        role_id=role_id,
        department=department,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Retrieve details for a specific user ID."
)
async def get_user_by_id(
    user_id: str,
    current_user: dict[str, Any] = Depends(get_current_user)
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found."
        )

    # Allow users to view themselves or admins to view within tenant
    if current_user["user_id"] != user_id and current_user.get("role_id") != SystemRole.ROLE_SUPER_ADMIN:
        if current_user.get("tenant_id") and user.tenant_id and current_user.get("tenant_id") != user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to users outside your tenant."
            )

    return user

