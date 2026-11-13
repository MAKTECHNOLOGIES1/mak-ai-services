"""
Pydantic Schemas for Identity Service (Validation & DTOs)
All IDs are customized strings (ZERO random UUIDs)
- user_id: Student Roll Number or Staff ID
- tenant_id: Custom College Code (e.g. "SRIT-ATP")
- role_id: Meaningful Role ID (e.g. "ROLE_STUDENT")
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -------------------------------------------------------------
# 1. Role Schemas
# -------------------------------------------------------------
class RoleBase(BaseModel):
    role_id: str | None = Field(
        None,
        example="ROLE_SR_LEAD",
        description="Custom role ID. If omitted, will be auto-generated from name.",
    )
    name: str = Field(..., example="Senior Technical Lead", description="Human-readable title")
    description: str | None = None
    hierarchy_level: int = Field(default=50, ge=1, le=100, description="Higher number = higher authority")
    is_self_registerable: bool = Field(default=False, description="Whether public registration is allowed")
    permissions: list[str] = Field(default_factory=list, example=["projects:verify", "code:review"])


class RoleCreate(RoleBase):
    pass


class RoleResponse(BaseModel):
    role_id: str
    name: str
    description: str | None = None
    hierarchy_level: int
    is_self_registerable: bool
    is_active: bool
    permissions: list[str] = Field(default_factory=list)
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------
# 2. Registration Schemas (Only Students Can Self-Register)
# -------------------------------------------------------------
class StudentRegisterRequest(BaseModel):
    tenant_id: str = Field(..., example="SRIT-ATP", description="Custom College ID / Code")
    roll_number: str = Field(
        ...,
        example="22731A0501",
        description="Student Roll Number — THIS IS THE USER_ID USED ACROSS ALL SERVICES",
    )
    email: EmailStr = Field(..., example="rahul.cse@srit.ac.in")
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: str = Field(..., example="Rahul Sharma")
    department: str = Field(..., example="CSE", description="Department code")
    batch_year: str = Field(..., example="2022-2026", description="Academic batch")


# -------------------------------------------------------------
# 3. Staff / Faculty / Manager Provisioning (Admin Provisioned)
# -------------------------------------------------------------
class AdminUserProvisionRequest(BaseModel):
    role_id: str = Field(..., example="ROLE_FACULTY", description="Target role ID (e.g. ROLE_FACULTY, ROLE_HOD, ROLE_TRAINER)")
    staff_id: str | None = Field(
        None,
        example="FAC-SRIT-001",
        description="Standard Employee/Staff ID. If left blank, a standard ID will be auto-generated.",
    )
    email: EmailStr = Field(..., example="prof.sreenivas@srit.ac.in")
    initial_password: str = Field(..., min_length=8, description="Initial password set by Admin")
    full_name: str = Field(..., example="Dr. K. Sreenivasulu")
    department: str = Field(..., example="CSE")


# -------------------------------------------------------------
# 4. Login & Token Schemas
# -------------------------------------------------------------
class UserLoginRequest(BaseModel):
    login_identifier: str | None = Field(None, example="22731A0501", description="Email or user_id (Roll number / Staff ID)")
    username: str | None = Field(None, example="22731A0501", description="Alias for login_identifier")
    email: str | None = Field(None, example="student@srit.ac.in", description="Alias for email login")
    roll_number: str | None = Field(None, example="22731A0501", description="Alias for roll number login")
    password: str = Field(..., example="Password123!")

    def get_identifier(self) -> str:
        ident = self.login_identifier or self.username or self.email or self.roll_number
        if not ident or not ident.strip():
            raise ValueError("Please provide your Roll Number, Staff ID, or Email to login.")
        return ident.strip()


class UserResponse(BaseModel):
    user_id: str = Field(..., description="Student Roll Number or Staff ID used platform-wide")
    tenant_id: str = Field(..., description="Custom College ID (e.g. SRIT-ATP)")
    email: EmailStr
    full_name: str
    department: str
    batch_year: str | None = None
    role_id: str
    role_name: str | None = None
    is_active: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
