"""
Dynamic Role Management API Endpoints
Cloudflare Workers compatible via Supabase PostgREST
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from core.database import SupabaseClient, get_db
from core.dependencies import require_min_hierarchy
from schemas.auth_schemas import RoleCreate, RoleResponse
from services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Dynamic Roles"])


@router.get(
    "",
    response_model=list[RoleResponse],
    summary="List All System Roles",
    description="Returns all active roles with their hierarchy levels and permissions.",
)
async def list_roles(
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    return await RoleService.get_all_roles(db)


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Dynamic Role",
    description="Allows Administrators (Level >= 90) to dynamically create new roles.",
)
async def create_role(
    payload: RoleCreate,
    current_user: dict[str, Any] = Depends(require_min_hierarchy(min_level=90)),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not configured.")
    try:
        return await RoleService.create_dynamic_role(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
