"""
Pydantic Schemas for Tenant Modules and Seat Quota Validation
"""

from typing import Optional
from pydantic import BaseModel, Field

class ModuleToggleRequest(BaseModel):
    module_key: str = Field(..., example="PROJECT_STUDIO")
    is_enabled: bool = Field(..., example=True)

class ModuleResponse(BaseModel):
    module_key: str
    is_enabled: bool

class SeatCheckRequest(BaseModel):
    tenant_id: str = Field(..., example="SRIT-ATP")
    role_id: str = Field(..., example="ROLE_STUDENT")

class SeatCheckResponse(BaseModel):
    tenant_id: str
    role_id: str
    allowed: bool
    current_count: int
    max_limit: int
    remaining_seats: int
    message: str

class SeatIncrementRequest(BaseModel):
    tenant_id: str = Field(..., example="SRIT-ATP")
    role_id: str = Field(..., example="ROLE_STUDENT")
    count: int = Field(default=1, ge=1)

class SeatIncrementResponse(BaseModel):
    success: bool
    tenant_id: str
    role_id: str
    current_students: int
    current_faculty: int
    message: str

