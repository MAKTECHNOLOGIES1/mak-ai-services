"""
Pydantic Schemas for Tenant College Management
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class TenantCreate(BaseModel):
    tenant_id: str = Field(..., min_length=2, max_length=50, example="SRIT-ATP")
    name: str = Field(..., min_length=3, max_length=255, example="Srinivasa Ramanujan Institute of Technology")
    university_affiliation: str = Field(default="JNTUA", example="JNTUA")
    tier: str = Field(default="STARTER", example="STARTER")
    max_students: int = Field(default=60, ge=1)
    max_faculty: int = Field(default=5, ge=1)
    monthly_ai_token_quota: int = Field(default=5000000, ge=100000)
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    enabled_modules: List[str] = Field(
        default=["COLLEGE_AI", "FACULTY_AI", "PROJECT_STUDIO", "RAG_SYLLABUS"]
    )

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    university_affiliation: Optional[str] = None
    tier: Optional[str] = None
    max_students: Optional[int] = Field(default=None, ge=1)
    max_faculty: Optional[int] = Field(default=None, ge=1)
    monthly_ai_token_quota: Optional[int] = Field(default=None, ge=100000)
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    university_affiliation: str
    tier: str
    max_students: int
    current_students: int
    max_faculty: int
    current_faculty: int
    monthly_ai_token_quota: int
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    is_active: bool
    enabled_modules: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TenantStatsResponse(BaseModel):
    tenant_id: str
    name: str
    tier: str
    student_seats_used: int
    student_seats_max: int
    student_utilization_pct: float
    faculty_seats_used: int
    faculty_seats_max: int
    faculty_utilization_pct: float
    is_capacity_warning: bool
    monthly_ai_token_quota: int
    is_active: bool

