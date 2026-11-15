"""
Authentication & Provisioning API Endpoints
Cloudflare Workers compatible via Supabase PostgREST
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import SupabaseClient, get_db
from core.dependencies import get_current_user, require_min_hierarchy
from schemas.auth_schemas import (
    AdminUserProvisionRequest,
    StudentRegisterRequest,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Provisioning"])


@router.post(
    "/register/student",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Student Self-Registration",
    description="Public self-registration strictly for STUDENTS. The student's Roll Number becomes their universal user_id.",
)
async def register_student(
    payload: StudentRegisterRequest,
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    return await AuthService.register_student(db, payload)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def register_student_alias(
    payload: StudentRegisterRequest,
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """Alias for /register/student"""
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    return await AuthService.register_student(db, payload)


@router.post(
    "/provision-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin / Manager User Provisioning",
    description="Authorized creation of non-student roles using custom role_id (e.g. 'ROLE_FACULTY', 'ROLE_HOD').",
)
@router.post(
    "/provision",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def provision_user(
    payload: AdminUserProvisionRequest,
    current_user: dict[str, Any] = Depends(require_min_hierarchy(min_level=70)),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    return await AuthService.provision_user_by_admin(db, payload, current_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Unified Login Endpoint",
    description="Authenticates any user by either Email OR user_id (Roll number / Staff ID) and returns JWT token.",
)
async def login(
    payload: UserLoginRequest,
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    return await AuthService.login_user(db, payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
)
async def get_my_profile(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    role_name = current_user.get("role_id")
    if db:
        from services.role_service import RoleService
        role = await RoleService.get_role_by_id(db, current_user.get("role_id", ""))
        if role:
            role_name = role.get("name")

    return UserResponse(
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        department=current_user.get("department", "GENERAL"),
        batch_year=current_user.get("batch_year"),
        role_id=current_user["role_id"],
        role_name=role_name,
        is_active=current_user.get("is_active", True),
        created_at=current_user.get("created_at"),
    )
