"""
Tenant HTTP API Router
Handles college profiles, seat stats, and feature module enablement.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.database import SupabaseClient, get_db
from core.dependencies import (
    get_current_user_claims,
    require_roles,
    verify_tenant_isolation,
)
from schemas.module_schemas import ModuleResponse, ModuleToggleRequest
from schemas.tenant_schemas import (
    TenantCreate,
    TenantResponse,
    TenantStatsResponse,
    TenantUpdate,
)
from services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/current", response_model=TenantResponse)
async def get_current_tenant(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Returns the college tenant profile for the currently authenticated user
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")
    tenant_id = claims["tenant_id"]
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found.",
        )
    return tenant


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    claims: dict[str, Any] = Depends(require_roles(["SUPERADMIN", "ADMIN"])),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    List registered institutional tenants.
    If caller is SUPERADMIN, lists all colleges.
    If caller is College ADMIN, returns only their own college.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")

    if claims["role_id"].upper() == "ROLE_SUPERADMIN":
        return await TenantService.list_tenants(db, skip=skip, limit=limit)

    # Restrict regular admin to their own tenant
    tenant = await TenantService.get_tenant_by_id(db, claims["tenant_id"])
    return [tenant] if tenant else []


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def onboard_college(
    payload: TenantCreate,
    claims: dict[str, Any] = Depends(require_roles(["SUPERADMIN"])),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Onboard a new college tenant with specified seat caps and tier.
    Requires ROLE_SUPERADMIN.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")
    try:
        return await TenantService.create_tenant(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant_details(
    tenant_id: str,
    claims: dict[str, Any] = Depends(verify_tenant_isolation),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Get detailed college profile with multi-tenant isolation guard
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found.",
        )
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant_details(
    tenant_id: str,
    payload: TenantUpdate,
    claims: dict[str, Any] = Depends(require_roles(["SUPERADMIN", "ADMIN"])),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Update college profile, seat caps, or branding
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")

    # Enforce isolation: College Admin can only modify their own tenant
    if claims["role_id"].upper() != "ROLE_SUPERADMIN" and claims["tenant_id"].upper() != tenant_id.upper():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update details for a different college tenant.",
        )

    # Only SUPERADMIN can change tiers or seat caps
    if claims["role_id"].upper() != "ROLE_SUPERADMIN":
        if payload.tier is not None or payload.max_students is not None or payload.max_faculty is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPERADMIN can adjust subscription tiers or maximum seat caps.",
            )

    updated = await TenantService.update_tenant(db, tenant_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found.",
        )
    return updated


@router.get("/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_statistics(
    tenant_id: str,
    claims: dict[str, Any] = Depends(verify_tenant_isolation),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Returns live seat utilization metrics and capacity warning flag
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")
    stats = await TenantService.get_tenant_stats(db, tenant_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found.",
        )
    return stats


@router.get("/{tenant_id}/modules", response_model=List[str])
async def list_tenant_modules(
    tenant_id: str,
    claims: dict[str, Any] = Depends(verify_tenant_isolation),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Returns list of active feature module keys for this college
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")
    return await TenantService.get_tenant_modules(db, tenant_id)


@router.post("/{tenant_id}/modules/toggle", response_model=List[str])
async def toggle_tenant_module(
    tenant_id: str,
    payload: ModuleToggleRequest,
    claims: dict[str, Any] = Depends(require_roles(["SUPERADMIN", "ADMIN"])),
    db: Optional[SupabaseClient] = Depends(get_db),
):
    """
    Enable or disable an AI feature module for this tenant
    """
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured.")

    if claims["role_id"].upper() != "ROLE_SUPERADMIN" and claims["tenant_id"].upper() != tenant_id.upper():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify module settings for another college tenant.",
        )

    return await TenantService.toggle_module(db, tenant_id, payload.module_key, payload.is_enabled)
