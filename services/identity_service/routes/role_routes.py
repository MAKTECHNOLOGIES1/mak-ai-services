"""
Dynamic Role Management API Endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from core.dependencies import require_min_hierarchy
from models.user_model import User
from schemas.auth_schemas import RoleCreate, RoleResponse
from services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Dynamic Roles"])

@router.get(
    "",
    response_model=List[RoleResponse],
    summary="List All System Roles",
    description="Returns all active roles with their hierarchy levels and permissions."
)
async def list_roles(
    db: AsyncSession = Depends(get_db)
):
    return await RoleService.get_all_roles(db)

@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Dynamic Role",
    description="Allows Administrators (Level >= 90) to dynamically create new roles (e.g. LAB_ASSISTANT, DEAN, etc.)."
)
async def create_role(
    payload: RoleCreate,
    current_user: User = Depends(require_min_hierarchy(min_level=90)), # Level 90 = ADMIN / SUPER_ADMIN
    db: AsyncSession = Depends(get_db)
):
    return await RoleService.create_dynamic_role(db, payload)

