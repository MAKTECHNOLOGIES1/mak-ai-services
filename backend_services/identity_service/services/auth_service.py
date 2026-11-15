"""
Authentication & User Provisioning Service for Identity Service
Cloudflare Workers compatible via Supabase PostgREST Client
ZERO Random UUIDs:
- user_id is the primary identifier (Roll Number for students, Staff ID for staff)
- tenant_id is the custom college code ("SRIT-ATP")
- role_id is the meaningful role ID ("ROLE_STUDENT", "ROLE_FACULTY")
"""

import uuid
from typing import Any
from fastapi import HTTPException, status

from core.config import settings
from core.database import SupabaseClient
from core.security import create_access_token, hash_password, verify_password
from models.tenant_model import tenant_from_row
from models.user_model import user_from_row
from schemas.auth_schemas import (
    AdminUserProvisionRequest,
    StudentRegisterRequest,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)
from services.role_service import RoleService


class AuthService:
    @staticmethod
    async def register_student(db: SupabaseClient, payload: StudentRegisterRequest) -> UserResponse:
        """
        Public self-registration for STUDENTS ONLY.
        - user_id = Roll Number (e.g. "22731A0501")
        - tenant_id = College Code (e.g. "SRIT-ATP")
        - role_id = "ROLE_STUDENT"
        """
        student_user_id = payload.roll_number.strip().upper()
        custom_tenant_id = payload.tenant_id.strip().upper()

        # 1. Look up college tenant by custom tenant_id
        tenant_row = await db.select("tenants", filters={"tenant_id": f"eq.{custom_tenant_id}"}, single=True)
        if not tenant_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College ID '{custom_tenant_id}' not found. Please verify with your coordinator."
            )

        tenant = tenant_from_row(tenant_row)
        if not tenant.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This college subscription is currently inactive."
            )

        # 2. Check student seat cap
        cur_students = tenant.get("current_students", 0)
        max_students = tenant.get("max_students", 60)
        if cur_students >= max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student seat limit reached ({cur_students}/{max_students}) for this college."
            )

        # 3. Check duplicate user_id (roll number)
        existing_uid = await db.select(
            "users",
            filters={"tenant_id": f"eq.{custom_tenant_id}", "user_id": f"eq.{student_user_id}"},
            single=True
        )
        if existing_uid:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student Roll Number '{student_user_id}' is already registered in this college."
            )

        # Check duplicate email
        existing_email = await db.select(
            "users",
            filters={"tenant_id": f"eq.{custom_tenant_id}", "email": f"eq.{payload.email.lower()}"},
            single=True
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already registered in this college."
            )

        # 4. Verify ROLE_STUDENT exists
        student_role = await RoleService.get_role_by_id(db, "ROLE_STUDENT")
        if not student_role:
            # Auto-seed if missing
            await RoleService.seed_default_roles_if_missing(db)
            student_role = await RoleService.get_role_by_id(db, "ROLE_STUDENT")

        # 5. Create Student User (ZERO Random UUIDs)
        new_user_data = {
            "user_id": student_user_id,
            "tenant_id": custom_tenant_id,
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.password),
            "full_name": payload.full_name.strip(),
            "department": payload.department.strip().upper(),
            "batch_year": payload.batch_year.strip(),
            "role_id": "ROLE_STUDENT",
            "created_by_user_id": None,
            "is_active": True,
        }

        inserted = await db.insert("users", new_user_data)
        if not inserted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register student record."
            )

        # 6. Increment current_students counter
        await db.update(
            "tenants",
            filters={"tenant_id": f"eq.{custom_tenant_id}"},
            values={"current_students": cur_students + 1}
        )

        user_dict = user_from_row(inserted)
        resp = UserResponse(
            user_id=user_dict["user_id"],
            tenant_id=user_dict["tenant_id"],
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            department=user_dict["department"],
            batch_year=user_dict.get("batch_year"),
            role_id=user_dict["role_id"],
            role_name=student_role["name"] if student_role else "Enrolled Student",
            is_active=user_dict["is_active"],
            created_at=user_dict.get("created_at"),
        )
        return resp

    @staticmethod
    async def provision_user_by_admin(
        db: SupabaseClient,
        payload: AdminUserProvisionRequest,
        creator: dict[str, Any]
    ) -> UserResponse:
        """
        Admin provisioned creation for staff/faculty.
        Uses custom staff_id, creator's tenant_id, and custom role_id.
        """
        clean_role_id = payload.role_id.strip().upper()
        if not clean_role_id.startswith("ROLE_"):
            clean_role_id = f"ROLE_{clean_role_id}"

        # 1. Fetch target role by role_id
        target_role = await RoleService.get_role_by_id(db, clean_role_id)
        if not target_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target role ID '{clean_role_id}' does not exist."
            )

        # 2. Check authority: Creator must have higher hierarchy than the target role
        creator_role_id = creator.get("role_id", "")
        creator_level = 100 if creator_role_id in ["ROLE_SUPER_ADMIN", "ROLE_SUPERADMIN"] else 0
        if creator_level < 100:
            creator_role = await RoleService.get_role_by_id(db, creator_role_id)
            creator_level = creator_role.get("hierarchy_level", 0) if creator_role else 0

        target_level = target_role.get("hierarchy_level", 0)
        if creator_level <= target_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to provision a role with level {target_level}. Your level is {creator_level}."
            )

        # 3. Determine Standard Staff user_id
        creator_tenant_id = creator.get("tenant_id") or settings.DEFAULT_TENANT_ID
        if payload.staff_id and payload.staff_id.strip():
            staff_user_id = payload.staff_id.strip().upper()
        else:
            prefix = clean_role_id.replace("ROLE_", "")[:3]
            random_suffix = str(uuid.uuid4())[:5].upper()
            staff_user_id = f"{prefix}-{creator_tenant_id}-{random_suffix}"

        # 4. Check duplicate user_id or email
        existing_uid = await db.select(
            "users",
            filters={"tenant_id": f"eq.{creator_tenant_id}", "user_id": f"eq.{staff_user_id}"},
            single=True
        )
        if existing_uid:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User ID '{staff_user_id}' already exists."
            )

        existing_email = await db.select(
            "users",
            filters={"tenant_id": f"eq.{creator_tenant_id}", "email": f"eq.{payload.email.lower()}"},
            single=True
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' already exists in this college."
            )

        # 5. Check faculty seat caps if role is ROLE_FACULTY
        if clean_role_id == "ROLE_FACULTY":
            tenant_row = await db.select("tenants", filters={"tenant_id": f"eq.{creator_tenant_id}"}, single=True)
            if tenant_row:
                tenant = tenant_from_row(tenant_row)
                cur_fac = tenant.get("current_faculty", 0)
                max_fac = tenant.get("max_faculty", 5)
                if cur_fac >= max_fac:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Faculty seat limit reached ({cur_fac}/{max_fac}) for this college."
                    )
                await db.update(
                    "tenants",
                    filters={"tenant_id": f"eq.{creator_tenant_id}"},
                    values={"current_faculty": cur_fac + 1}
                )

        # 6. Create User (ZERO Random UUIDs)
        new_staff_data = {
            "user_id": staff_user_id,
            "tenant_id": creator_tenant_id,
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.initial_password),
            "full_name": payload.full_name.strip(),
            "department": payload.department.strip().upper(),
            "role_id": target_role["role_id"],
            "created_by_user_id": creator.get("user_id"),
            "is_active": True,
        }

        inserted = await db.insert("users", new_staff_data)
        if not inserted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to provision staff record."
            )

        user_dict = user_from_row(inserted)
        return UserResponse(
            user_id=user_dict["user_id"],
            tenant_id=user_dict["tenant_id"],
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            department=user_dict["department"],
            batch_year=user_dict.get("batch_year"),
            role_id=user_dict["role_id"],
            role_name=target_role.get("name"),
            is_active=user_dict["is_active"],
            created_at=user_dict.get("created_at"),
        )

    @staticmethod
    async def login_user(db: SupabaseClient, payload: UserLoginRequest) -> TokenResponse:
        """
        Unified Login: Users can login with EITHER their Email OR their user_id (Roll number / Staff ID).
        """
        identifier = payload.get_identifier()

        # Try user_id match first (case-insensitive upper)
        user_row = await db.select(
            "users",
            filters={"user_id": f"eq.{identifier.upper()}"},
            single=True
        )

        # Try raw user_id if not found
        if not user_row:
            user_row = await db.select(
                "users",
                filters={"user_id": f"eq.{identifier}"},
                single=True
            )

        # Try email match if still not found
        if not user_row:
            user_row = await db.select(
                "users",
                filters={"email": f"eq.{identifier.lower()}"},
                single=True
            )

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No account found with identifier '{identifier}'. Please check your Roll Number or Email."
            )

        user = user_from_row(user_row)

        if not verify_password(payload.password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Please verify the credentials you entered."
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Please contact your administrator."
            )

        role = await RoleService.get_role_by_id(db, user["role_id"])
        role_name = role.get("name") if role else user["role_id"]

        # Generate JWT Token
        access_token = create_access_token(
            subject=user["user_id"],
            tenant_id=user["tenant_id"],
            role=user["role_id"],
            extra_claims={
                "role_name": role_name,
                "email": user["email"],
                "department": user.get("department", "GENERAL"),
                "full_name": user.get("full_name", "")
            }
        )

        user_resp = UserResponse(
            user_id=user["user_id"],
            tenant_id=user["tenant_id"],
            email=user["email"],
            full_name=user["full_name"],
            department=user.get("department", "GENERAL"),
            batch_year=user.get("batch_year"),
            role_id=user["role_id"],
            role_name=role_name,
            is_active=user["is_active"],
            created_at=user.get("created_at"),
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp
        )
