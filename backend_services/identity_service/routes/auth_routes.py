"""
Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user, require_min_hierarchy
from models.user_model import User
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
    db: AsyncSession = Depends(get_db),
):
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
    current_user: User = Depends(require_min_hierarchy(min_level=70)),  # HOD/Manager/Admin
    db: AsyncSession = Depends(get_db),
):
    return await AuthService.provision_user_by_admin(db, payload, current_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Unified Login Endpoint",
    description="Authenticates any user by either Email OR user_id (Roll number / Staff ID) and returns JWT token.",
)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await AuthService.login_user(db, payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    resp = UserResponse.model_validate(current_user)
    if current_user.role:
        resp.role_name = current_user.role.name
    return resp
