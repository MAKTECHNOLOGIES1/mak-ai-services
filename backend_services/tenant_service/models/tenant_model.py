"""
Tenant Model for Tenant Service
Directly maps to identity_service.tenants table in Supabase PostgreSQL
"""

from typing import ClassVar
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from core.database import Base
from models.module_model import TenantModule

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "identity_service"}

    # Unique meaningful college code (e.g. "SRIT-ATP", "JNTUA-CEA")
    tenant_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    university_affiliation = Column(String(100), default="JNTUA")
    tier = Column(String(50), default="STARTER") # 'STARTER', 'PRO', 'ENTERPRISE'
    
    # Hard seat caps for license governance
    max_students = Column(Integer, default=60, nullable=False)
    max_faculty = Column(Integer, default=5, nullable=False)
    current_students = Column(Integer, default=0, nullable=False)
    current_faculty = Column(Integer, default=0, nullable=False)

    # Monthly AI Token Quota allocated to this college
    monthly_ai_token_quota = Column(BigInteger, default=5000000, nullable=False)

    # Branding & Contact
    logo_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    modules = relationship("TenantModule", back_populates="tenant", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self):
        return f"<Tenant id={self.tenant_id} name={self.name} tier={self.tier}>"

