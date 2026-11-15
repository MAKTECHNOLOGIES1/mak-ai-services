"""
Internal Microservice Routing for Tenant Service
Allows identity_service and other microservices to validate seat caps and update tallies
Protected via X-Internal-Service-Key or Admin Token
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import verify_service_or_admin
from schemas.module_schemas import (
    SeatCheckRequest,
    SeatCheckResponse,
    SeatIncrementRequest,
    SeatIncrementResponse
)
from services.seat_validator import SeatValidator

router = APIRouter(prefix="/tenants/internal", tags=["Internal Service Integration"])

@router.post("/check-seat", response_model=SeatCheckResponse)
async def check_seat_capacity(
    payload: SeatCheckRequest,
    auth: dict[str, Any] = Depends(verify_service_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Called by identity_service before registering a student or provisioning staff.
    Validates against hard seat caps.
    """
    return await SeatValidator.check_seat_availability(
        db=db,
        tenant_id=payload.tenant_id,
        role_id=payload.role_id
    )

@router.post("/increment-seat", response_model=SeatIncrementResponse)
async def increment_seat_allocation(
    payload: SeatIncrementRequest,
    auth: dict[str, Any] = Depends(verify_service_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Called by identity_service when a user account is committed to the database.
    Increments student or faculty counter.
    """
    success, curr_stu, curr_fac, msg = await SeatValidator.increment_seat_count(
        db=db,
        tenant_id=payload.tenant_id,
        role_id=payload.role_id,
        count=payload.count
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    return SeatIncrementResponse(
        success=True,
        tenant_id=payload.tenant_id,
        role_id=payload.role_id,
        current_students=curr_stu,
        current_faculty=curr_fac,
        message=msg
    )

@router.post("/decrement-seat", response_model=SeatIncrementResponse)
async def decrement_seat_allocation(
    payload: SeatIncrementRequest,
    auth: dict[str, Any] = Depends(verify_service_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Called when a student or staff member is removed.
    """
    success, curr_stu, curr_fac, msg = await SeatValidator.decrement_seat_count(
        db=db,
        tenant_id=payload.tenant_id,
        role_id=payload.role_id,
        count=payload.count
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    return SeatIncrementResponse(
        success=True,
        tenant_id=payload.tenant_id,
        role_id=payload.role_id,
        current_students=curr_stu,
        current_faculty=curr_fac,
        message=msg
    )

