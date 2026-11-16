"""
User Management Service for Identity Service
Handles admin user provisioning, profile lookups, and seat cap enforcement.
"""

import logging
from typing import Any, Optional
from fastapi import HTTPException, status

from core.database import supabase
from core.security import hash_password
from schemas.user_schemas import ProvisionUserRequest, UserResponse

logger = logging.getLogger(__name__)


class UserService:

    async def provision_user(
        self,
        admin_user: dict[str, Any],
        req: ProvisionUserRequest
    ) -> UserResponse:
        """
        Provision an official college staff/faculty/HOD account.
        Enforces tenant isolation and seat caps.
        """
        admin_role = admin_user.get("role_id")
        admin_tenant = admin_user.get("tenant_id")

        # 1. Tenant boundary enforcement
        if admin_role != "ROLE_SUPER_ADMIN" and admin_tenant != req.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot provision users outside your tenant '{admin_tenant}'."
            )

        # 2. Check if user_id or email already exists
        existing_id = await supabase.select(
            table="users",
            filters={"user_id": f"eq.{req.user_id.strip()}"},
            single=True
        )
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User ID '{req.user_id}' already exists."
            )

        existing_email = await supabase.select(
            table="users",
            filters={
                "tenant_id": f"eq.{req.tenant_id}",
                "email": f"eq.{req.email.strip().lower()}"
            },
            single=True
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{req.email}' is already registered in tenant '{req.tenant_id}'."
            )

        # 3. Check seat cap for faculty/staff
        tenant = await supabase.select(
            table="tenants",
            filters={"tenant_id": f"eq.{req.tenant_id}"},
            single=True
        )
        if tenant and "FACULTY" in req.role_id:
            current_fac = tenant.get("current_faculty", 0)
            max_fac = tenant.get("max_faculty", 10)
            if current_fac >= max_fac:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Faculty seat limit reached ({current_fac}/{max_fac}) for college '{req.tenant_id}'."
                )

        # 4. Create user record
        hashed_pw = hash_password(req.password)
        new_user = {
            "user_id": req.user_id.strip(),
            "tenant_id": req.tenant_id.strip(),
            "email": req.email.strip().lower(),
            "password_hash": hashed_pw,
            "full_name": req.full_name.strip(),
            "department": req.department.strip() if req.department else "GENERAL",
            "batch_year": None,
            "role_id": req.role_id.strip(),
            "created_by_user_id": admin_user.get("user_id"),
            "is_active": True
        }

        try:
            created = await supabase.insert("users", new_user)
        except Exception as e:
            logger.error("Failed to provision user: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to provision user: {str(e)}"
            )

        # Increment faculty counter if tenant exists
        if tenant and "FACULTY" in req.role_id:
            try:
                await supabase.update(
                    table="tenants",
                    data={"current_faculty": tenant.get("current_faculty", 0) + 1},
                    filters={"tenant_id": f"eq.{req.tenant_id}"}
                )
            except Exception as err:
                logger.warning("Could not update faculty count: %s", str(err))

        return UserResponse(
            user_id=new_user["user_id"],
            tenant_id=new_user["tenant_id"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            department=new_user["department"],
            batch_year=None,
            role_id=new_user["role_id"],
            is_active=True
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Fetch a single user profile."""
        user = await supabase.select(
            table="users",
            filters={"user_id": f"eq.{user_id}"},
            single=True
        )
        if not user:
            return None

        return UserResponse(
            user_id=user["user_id"],
            tenant_id=user.get("tenant_id"),
            email=user["email"],
            full_name=user.get("full_name", ""),
            department=user.get("department"),
            batch_year=user.get("batch_year"),
            role_id=user.get("role_id", "ROLE_STUDENT"),
            is_active=user.get("is_active", True),
            created_at=str(user.get("created_at")) if user.get("created_at") else None,
            updated_at=str(user.get("updated_at")) if user.get("updated_at") else None,
        )

    async def list_users(
        self,
        tenant_id: Optional[str] = None,
        role_id: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[UserResponse]:
        """List users matching filters."""
        filters: dict[str, str] = {}
        if tenant_id:
            filters["tenant_id"] = f"eq.{tenant_id}"
        if role_id:
            filters["role_id"] = f"eq.{role_id}"
        if department:
            filters["department"] = f"eq.{department}"

        raw_users = await supabase.select(
            table="users",
            filters=filters,
            order="created_at.desc",
            limit=limit,
            offset=offset
        )

        if not raw_users or not isinstance(raw_users, list):
            return []

        return [
            UserResponse(
                user_id=u["user_id"],
                tenant_id=u.get("tenant_id"),
                email=u["email"],
                full_name=u.get("full_name", ""),
                department=u.get("department"),
                batch_year=u.get("batch_year"),
                role_id=u.get("role_id", "ROLE_STUDENT"),
                is_active=u.get("is_active", True),
                created_at=str(u.get("created_at")) if u.get("created_at") else None,
                updated_at=str(u.get("updated_at")) if u.get("updated_at") else None,
            )
            for u in raw_users
        ]


user_service = UserService()

