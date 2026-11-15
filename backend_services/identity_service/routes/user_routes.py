"""
User Management API Endpoints
Cloudflare Workers compatible via Supabase PostgREST
All IDs are clean custom strings
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.database import SupabaseClient, get_db
from core.dependencies import require_min_hierarchy
from models.user_model import user_from_row
from schemas.auth_schemas import UserResponse
from services.role_service import RoleService

router = APIRouter(prefix="/users", tags=["Users Management"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List Users in Tenant",
    description="Returns users in current college. Filterable by role_id (e.g. ROLE_FACULTY), department, etc.",
)
async def list_tenant_users(
    role_id: str | None = Query(None, description="Filter by role_id (e.g. ROLE_STUDENT, ROLE_FACULTY)"),
    department: str | None = Query(None, description="Filter by department (e.g. CSE)"),
    current_user: dict[str, Any] = Depends(require_min_hierarchy(min_level=50)),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")

    filters: dict[str, str] = {"tenant_id": f"eq.{current_user['tenant_id']}"}
    if role_id:
        clean_role = role_id.upper() if role_id.upper().startswith("ROLE_") else f"ROLE_{role_id.upper()}"
        filters["role_id"] = f"eq.{clean_role}"
    if department:
        filters["department"] = f"eq.{department.upper()}"

    rows = await db.select("users", filters=filters, order="created_at.desc")

    response_list: list[UserResponse] = []
    roles = await RoleService.get_all_roles(db)
    role_map = {r.role_id: r.name for r in roles}

    for row in (rows or []):
        u = user_from_row(row)
        response_list.append(UserResponse(
            user_id=u["user_id"],
            tenant_id=u["tenant_id"],
            email=u["email"],
            full_name=u["full_name"],
            department=u.get("department", "GENERAL"),
            batch_year=u.get("batch_year"),
            role_id=u["role_id"],
            role_name=role_map.get(u["role_id"], u["role_id"]),
            is_active=u.get("is_active", True),
            created_at=u.get("created_at"),
        ))

    return response_list


@router.patch(
    "/{target_user_id}/status",
    response_model=UserResponse,
    summary="Activate / Deactivate User Account",
)
async def toggle_user_status(
    target_user_id: str,
    is_active: bool,
    current_user: dict[str, Any] = Depends(require_min_hierarchy(min_level=80)),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")

    clean_target_id = target_user_id.strip().upper()
    user_row = await db.select(
        "users",
        filters={
            "tenant_id": f"eq.{current_user['tenant_id']}",
            "user_id": f"eq.{clean_target_id}"
        },
        single=True
    )

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{target_user_id}' not found in college '{current_user['tenant_id']}'"
        )

    updated = await db.update(
        "users",
        filters={
            "tenant_id": f"eq.{current_user['tenant_id']}",
            "user_id": f"eq.{clean_target_id}"
        },
        values={"is_active": is_active}
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update status")

    u = user_from_row(updated)
    return UserResponse(
        user_id=u["user_id"],
        tenant_id=u["tenant_id"],
        email=u["email"],
        full_name=u["full_name"],
        department=u.get("department", "GENERAL"),
        batch_year=u.get("batch_year"),
        role_id=u["role_id"],
        role_name=u["role_id"],
        is_active=u.get("is_active", True),
        created_at=u.get("created_at"),
    )
