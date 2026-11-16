"""
Authentication Schemas for Identity Service
Defines schemas for login, direct student registration (no tenant assigned), and token operations.
"""

from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterStudentRequest(BaseModel):
    """
    Direct Student Self-Registration.
    No college code validation required.
    No tenant ID assigned (students are independent users).
    """
    roll_number: str = Field(..., min_length=3, max_length=100, description="Student Roll Number (becomes user_id)")
    full_name: str = Field(..., min_length=2, max_length=150, description="Full Name of the student")
    email: EmailStr = Field(..., description="Student email address")
    password: str = Field(..., min_length=6, max_length=128, description="Account password")
    department: Optional[str] = Field(default="GENERAL", max_length=50, description="Department (e.g. CSE, ECE)")
    batch_year: Optional[str] = Field(default=None, max_length=20, description="Batch year (e.g. 2022-2026)")


class LoginRequest(BaseModel):
    """User Login Request."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")
    tenant_id: Optional[str] = Field(default=None, description="Optional tenant ID (only required for college staff)")


class RefreshTokenRequest(BaseModel):
    """Token Refresh Request."""
    refresh_token: str = Field(..., description="Valid refresh token")


class UserProfile(BaseModel):
    """User profile data returned in authentication responses."""
    user_id: str
    tenant_id: Optional[str] = None
    email: str
    full_name: str
    department: Optional[str] = None
    batch_year: Optional[str] = None
    role_id: str
    is_active: bool = True


class TokenResponse(BaseModel):
    """JWT Token Response returned on login and student direct registration."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


class VerifyTokenRequest(BaseModel):
    """Internal token verification request for API Gateway."""
    token: str


class VerifyTokenResponse(BaseModel):
    """Internal token verification response."""
    valid: bool
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    role_id: Optional[str] = None
    email: Optional[str] = None
    error: Optional[str] = None

