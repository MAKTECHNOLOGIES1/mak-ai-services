"""
Authentication & User Provisioning Service
ZERO Random UUIDs:
- user_id is the primary identifier (Roll Number for students, Staff ID for staff)
- tenant_id is the custom college code ("SRIT-ATP")
- role_id is the meaningful role ID ("ROLE_STUDENT", "ROLE_FACULTY")
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_
from fastapi import HTTPException, status
import uuid
from core.security import hash_password, verify_password, create_access_token
from core.config import settings
from models.user_model import User
from models.role_model import Role
from models.tenant_model import Tenant
from schemas.auth_schemas import (
    StudentRegisterRequest,
    AdminUserProvisionRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse
)
from services.role_service import RoleService

class AuthService:

    @staticmethod
    async def register_student(db: AsyncSession, payload: StudentRegisterRequest) -> UserResponse:
        """
        Public self-registration for STUDENTS ONLY.
        - user_id = Roll Number (e.g. "22731A0501")
        - tenant_id = College Code (e.g. "SRIT-ATP")
        - role_id = "ROLE_STUDENT"
        """
        student_user_id = payload.roll_number.strip().upper()
        custom_tenant_id = payload.tenant_id.strip().upper()

        # 1. Look up college tenant by custom tenant_id
        result = await db.execute(
            select(Tenant).where(Tenant.tenant_id == custom_tenant_id)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College ID '{custom_tenant_id}' not found. Please verify with your coordinator."
            )

        if not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This college subscription is currently inactive."
            )

        # 2. Check student seat cap
        if tenant.current_students >= tenant.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student seat limit reached ({tenant.current_students}/{tenant.max_students}) for this college."
            )

        # 3. Check duplicate user_id (roll number) or email in this college
        existing_check = await db.execute(
            select(User).where(
                User.tenant_id == custom_tenant_id,
                or_(User.email == payload.email.lower(), User.user_id == student_user_id)
            )
        )
        existing = existing_check.scalar_one_or_none()
        if existing:
            if existing.user_id == student_user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Student Roll Number '{student_user_id}' is already registered in this college."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already registered in this college."
            )

        # 4. Verify ROLE_STUDENT exists
        student_role = await RoleService.get_role_by_id(db, "ROLE_STUDENT")
        if not student_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System error: ROLE_STUDENT is not initialized."
            )

        # 5. Create Student User (ZERO Random UUIDs)
        new_student = User(
            user_id=student_user_id,          # Custom Roll Number
            tenant_id=custom_tenant_id,       # Custom College Code ("SRIT-ATP")
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            department=payload.department.strip().upper(),
            batch_year=payload.batch_year.strip(),
            role_id="ROLE_STUDENT",           # Custom Role ID
            created_by_user_id=None,
            is_active=True
        )
        db.add(new_student)

        # 6. Increment current_students counter
        tenant.current_students += 1

        await db.commit()
        await db.refresh(new_student)

        resp = UserResponse.model_validate(new_student)
        resp.role_name = student_role.name
        return resp

    @staticmethod
    async def provision_user_by_admin(
        db: AsyncSession,
        payload: AdminUserProvisionRequest,
        creator: User
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
        creator_role = await RoleService.get_role_by_id(db, creator.role_id)
        creator_level = creator_role.hierarchy_level if creator_role else 0

        if creator_level <= target_role.hierarchy_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to provision a role with level {target_role.hierarchy_level}. Your level is {creator_level}."
            )

        # 3. Determine Standard Staff user_id
        if payload.staff_id and payload.staff_id.strip():
            staff_user_id = payload.staff_id.strip().upper()
        else:
            # Generate standard staff id: e.g. "FAC-SRIT-001"
            prefix = clean_role_id.replace("ROLE_", "")[:3]
            random_suffix = str(uuid.uuid4())[:5].upper()
            staff_user_id = f"{prefix}-{creator.tenant_id}-{random_suffix}"

        # 4. Check duplicate user_id or email
        existing_check = await db.execute(
            select(User).where(
                User.tenant_id == creator.tenant_id,
                or_(User.email == payload.email.lower(), User.user_id == staff_user_id)
            )
        )
        existing = existing_check.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{payload.email}' or user ID '{staff_user_id}' already exists."
            )

        # 5. Check faculty seat caps if role is ROLE_FACULTY
        if clean_role_id == "ROLE_FACULTY":
            tenant_res = await db.execute(select(Tenant).where(Tenant.tenant_id == creator.tenant_id))
            tenant = tenant_res.scalar_one_or_none()
            if tenant and tenant.current_faculty >= tenant.max_faculty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Faculty seat limit reached ({tenant.current_faculty}/{tenant.max_faculty}) for this college."
                )
            if tenant:
                tenant.current_faculty += 1

        # 6. Create User (ZERO Random UUIDs)
        new_staff = User(
            user_id=staff_user_id,             # Custom Staff ID
            tenant_id=creator.tenant_id,       # Same custom college code as creator
            email=payload.email.lower(),
            password_hash=hash_password(payload.initial_password),
            full_name=payload.full_name.strip(),
            department=payload.department.strip().upper(),
            role_id=target_role.role_id,       # Meaningful Role ID
            created_by_user_id=creator.user_id,# Admin's own user_id!
            is_active=True
        )
        db.add(new_staff)
        await db.commit()
        await db.refresh(new_staff)

        resp = UserResponse.model_validate(new_staff)
        resp.role_name = target_role.name
        return resp

    @staticmethod
    async def login_user(db: AsyncSession, payload: UserLoginRequest) -> TokenResponse:
        """
        Unified Login: Users can login with EITHER their Email OR their user_id (Roll number / Staff ID)!
        Supports flexible alias fields: login_identifier, username, email, or roll_number.
        """
        identifier = payload.get_identifier()

        result = await db.execute(
            select(User).where(
                or_(
                    User.email == identifier.lower(),
                    User.user_id == identifier.upper(),
                    User.user_id == identifier
                )
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No account found with identifier '{identifier}'. Please check your Roll Number or Email."
            )

        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Please verify the password you entered during registration."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Please contact your administrator."
            )

        role = await RoleService.get_role_by_id(db, user.role_id)
        role_name = role.name if role else user.role_id

        # Generate JWT Token: 'sub' contains the standard user_id
        access_token = create_access_token(
            subject=user.user_id, # "22731A0501" or "FAC-SRIT-001"
            tenant_id=user.tenant_id, # "SRIT-ATP"
            role=user.role_id, # "ROLE_STUDENT", "ROLE_FACULTY"
            extra_claims={
                "role_name": role_name,
                "email": user.email,
                "department": user.department,
                "full_name": user.full_name
            }
        )

        user_resp = UserResponse.model_validate(user)
        user_resp.role_name = role_name

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp
        )
