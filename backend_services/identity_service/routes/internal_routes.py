"""
Internal Routes for Identity Service
Inter-service endpoints consumed by API Gateway and peer backend services.
Protected by X-Internal-Service-Key authentication header.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError

from core.database import supabase
from core.dependencies import verify_internal_key
from core.security import decode_token
from schemas.auth_schemas import VerifyTokenRequest, VerifyTokenResponse
from schemas.user_schemas import UserResponse
from services.user_service import user_service

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post(
    "/verify-token",
    response_model=VerifyTokenResponse,
    summary="Internal Token Verification",
    description="Validates a JWT token on behalf of the API Gateway or peer services."
)
async def verify_token(
    req: VerifyTokenRequest,
    _authorized: bool = Depends(verify_internal_key)
):
    try:
        payload = decode_token(req.token)
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            return VerifyTokenResponse(valid=False, error="Token missing subject identifier")

        # Verify active user in DB
        user = await supabase.select(
            table="users",
            filters={"user_id": f"eq.{user_id}"},
            single=True
        )

        if not user or not user.get("is_active", True):
            return VerifyTokenResponse(valid=False, error="User account inactive or not found")

        return VerifyTokenResponse(
            valid=True,
            user_id=user["user_id"],
            tenant_id=user.get("tenant_id"),
            role_id=user.get("role_id"),
            email=user.get("email")
        )
    except JWTError as e:
        return VerifyTokenResponse(valid=False, error=str(e))
    except Exception as e:
        return VerifyTokenResponse(valid=False, error=f"Verification error: {str(e)}")


@router.get(
    "/user/{user_id}",
    response_model=UserResponse,
    summary="Internal User Lookup",
    description="Fetches user details by user_id for peer backend services."
)
async def get_internal_user(
    user_id: str,
    _authorized: bool = Depends(verify_internal_key)
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found."
        )
    return user

