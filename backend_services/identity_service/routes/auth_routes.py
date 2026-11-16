"""
Authentication Routes for Identity Service
Public and self-service authentication endpoints:
- POST /api/v1/auth/register/student (Direct registration, no tenant assigned)
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- GET  /api/v1/auth/me
"""

from typing import Any
from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user
from schemas.auth_schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterStudentRequest,
    TokenResponse,
    UserProfile
)
from services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/student",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Direct Student Registration",
    description="Registers a student directly without college code validation and without assigning a tenant ID. Immediately returns JWT tokens."
)
async def register_student(req: RegisterStudentRequest):
    return await auth_service.register_student(req)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates users (students or staff) and issues access and refresh tokens."
)
async def login(req: LoginRequest):
    return await auth_service.login(req)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
    description="Issues new access and refresh tokens using a valid refresh token."
)
async def refresh_token(req: RefreshTokenRequest):
    return await auth_service.refresh_tokens(req.refresh_token)


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Current User Profile",
    description="Returns the profile information of the currently authenticated user."
)
async def get_me(current_user: dict[str, Any] = Depends(get_current_user)):
    return UserProfile(
        user_id=current_user["user_id"],
        tenant_id=current_user.get("tenant_id"),
        email=current_user["email"],
        full_name=current_user.get("full_name", ""),
        department=current_user.get("department"),
        batch_year=current_user.get("batch_year"),
        role_id=current_user.get("role_id", "ROLE_STUDENT"),
        is_active=current_user.get("is_active", True)
    )

