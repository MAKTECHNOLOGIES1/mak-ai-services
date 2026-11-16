"""
Authentication Service for Identity Service
Handles direct student onboarding (no tenant assigned), credential verification,
and token issuance and refresh.
"""

import logging
from typing import Any
from fastapi import HTTPException, status

from core.config import settings
from core.database import supabase
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password
)
from schemas.auth_schemas import (
    LoginRequest,
    RegisterStudentRequest,
    TokenResponse,
    UserProfile
)

logger = logging.getLogger(__name__)


class AuthService:

    async def register_student(self, req: RegisterStudentRequest) -> TokenResponse:
        """
        Direct Student Self-Registration.
        - No college code validation.
        - Students are registered directly with NO tenant_id assigned (tenant_id = None).
        - Instantly returns access & refresh tokens for frictionless immediate onboarding.
        """
        roll_number = req.roll_number.strip().upper()
        email = req.email.strip().lower()

        # 1. Check if roll number (user_id) already exists
        existing_user_id = await supabase.select(
            table="users",
            filters={"user_id": f"eq.{roll_number}"},
            single=True
        )
        if existing_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student roll number '{roll_number}' is already registered."
            )

        # 2. Check if email already exists
        existing_email = await supabase.select(
            table="users",
            filters={"email": f"eq.{email}"},
            single=True
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email address '{email}' is already registered."
            )

        # 3. Hash password securely (pure Python / PBKDF2 edge-compatible)
        hashed_pw = hash_password(req.password)

        # 4. Insert student record into identity_service.users
        # tenant_id is explicitly set to None (no tenant assigned)
        user_record: dict[str, Any] = {
            "user_id": roll_number,
            "tenant_id": None,
            "email": email,
            "password_hash": hashed_pw,
            "full_name": req.full_name.strip(),
            "department": req.department.strip() if req.department else "GENERAL",
            "batch_year": req.batch_year.strip() if req.batch_year else None,
            "role_id": "ROLE_STUDENT",
            "is_active": True
        }

        try:
            created_user = await supabase.insert("users", user_record)
        except Exception as e:
            logger.error("Failed to insert student user: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to register student: {str(e)}"
            )

        # 5. Generate Access & Refresh Tokens immediately
        token_payload = {
            "sub": roll_number,
            "user_id": roll_number,
            "email": email,
            "role_id": "ROLE_STUDENT",
            "tenant_id": None,
            "department": user_record["department"]
        }
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token({"sub": roll_number, "user_id": roll_number, "tenant_id": None})

        profile = UserProfile(
            user_id=roll_number,
            tenant_id=None,
            email=email,
            full_name=user_record["full_name"],
            department=user_record["department"],
            batch_year=user_record["batch_year"],
            role_id="ROLE_STUDENT",
            is_active=True
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=profile
        )

    async def login(self, req: LoginRequest) -> TokenResponse:
        """
        Authenticate user with email and password.
        Supports both independent students (no tenant_id) and college staff (with tenant_id).
        """
        email = req.email.strip().lower()

        filters: dict[str, str] = {"email": f"eq.{email}"}
        if req.tenant_id:
            filters["tenant_id"] = f"eq.{req.tenant_id}"

        users = await supabase.select(table="users", filters=filters)
        if not users or len(users) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        user = users[0]

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated."
            )

        stored_hash = user.get("password_hash", "")
        if not verify_password(req.password, stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        user_id = user["user_id"]
        tenant_id = user.get("tenant_id")
        role_id = user.get("role_id", "ROLE_STUDENT")

        token_payload = {
            "sub": user_id,
            "user_id": user_id,
            "email": email,
            "role_id": role_id,
            "tenant_id": tenant_id,
            "department": user.get("department")
        }
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token({"sub": user_id, "user_id": user_id, "tenant_id": tenant_id})

        profile = UserProfile(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            full_name=user.get("full_name", ""),
            department=user.get("department"),
            batch_year=user.get("batch_year"),
            role_id=role_id,
            is_active=user.get("is_active", True)
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=profile
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Validate a refresh token and return fresh access and refresh tokens."""
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: refresh token expected."
            )

        user_id = payload.get("sub") or payload.get("user_id")
        user = await supabase.select(table="users", filters={"user_id": f"eq.{user_id}"}, single=True)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer active."
            )

        token_payload = {
            "sub": user["user_id"],
            "user_id": user["user_id"],
            "email": user["email"],
            "role_id": user.get("role_id"),
            "tenant_id": user.get("tenant_id"),
            "department": user.get("department")
        }
        new_access_token = create_access_token(token_payload)
        new_refresh_token = create_refresh_token({
            "sub": user["user_id"],
            "user_id": user["user_id"],
            "tenant_id": user.get("tenant_id")
        })

        profile = UserProfile(
            user_id=user["user_id"],
            tenant_id=user.get("tenant_id"),
            email=user["email"],
            full_name=user.get("full_name", ""),
            department=user.get("department"),
            batch_year=user.get("batch_year"),
            role_id=user.get("role_id", "ROLE_STUDENT"),
            is_active=user.get("is_active", True)
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=profile
        )


auth_service = AuthService()

