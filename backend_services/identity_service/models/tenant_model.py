"""
Tenant Model for Identity Service
Uses custom, meaningful tenant_id (e.g. "SRIT-ATP", "JNTUA-CEA")
"""

from typing import ClassVar

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "identity_service"}

    # Custom College Identifier (e.g. "SRIT-ATP")
    tenant_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    university_affiliation = Column(String(100), default="JNTUA")
    tier = Column(String(50), default="STARTER")
    max_students = Column(Integer, default=60)
    max_faculty = Column(Integer, default=5)
    current_students = Column(Integer, default=0)
    current_faculty = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Tenant tenant_id={self.tenant_id} name={self.name}>"
