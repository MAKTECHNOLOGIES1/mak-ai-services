"""
User Management Schemas for Identity Service
Defines schemas for admin user provisioning, profile updates, and user queries.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ProvisionUserRequest(BaseModel):
    """Admin provisioning request for faculty, staff, or department heads."""
    user_id: str = Field(..., min_length=3, max_length=100, description="Unique Staff/Faculty ID (e.g. FAC-SRIT-002)")
    email: EmailStr = Field(..., description="Staff official email address")
    password: str = Field(..., min_length=6, max_length=128, description="Initial temporary password")
    full_name: str = Field(..., min_length=2, max_length=150, description="Full Name")
    department: str = Field(default="GENERAL", max_length=50, description="Department code (CSE, ECE, EEE, etc.)")
    role_id: str = Field(..., description="Target role (e.g. ROLE_FACULTY, ROLE_HOD, ROLE_TRAINER)")
    tenant_id: str = Field(..., description="Tenant / College code to which the user belongs")


class UpdateUserRequest(BaseModel):
    """Profile update schema."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    department: Optional[str] = Field(None, max_length=50)
    batch_year: Optional[str] = Field(None, max_length=20)


class ChangePasswordRequest(BaseModel):
    """Change password schema."""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    """Detailed user response."""
    user_id: str
    tenant_id: Optional[str] = None
    email: str
    full_name: str
    department: Optional[str] = None
    batch_year: Optional[str] = None
    role_id: str
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

