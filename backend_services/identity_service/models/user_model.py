"""
User Model for Multi-Tenant Identity Service
- Fully customized IDs (ZERO random UUIDs):
  * user_id: Student Roll Number ("22731A0501") or Staff ID ("FAC-SRIT-001") as PRIMARY KEY
  * tenant_id: Custom College Code ("SRIT-ATP") referencing tenants.tenant_id
  * role_id: Meaningful Role ID ("ROLE_STUDENT", "ROLE_FACULTY") referencing roles.role_id
  * created_by_user_id: user_id of the admin who provisioned this account
"""

from typing import ClassVar

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "identity_service"}

    # PRIMARY KEY: Custom Universal user_id (Student Roll Number or Staff ID)
    user_id = Column(String(100), primary_key=True, index=True)

    # Custom College Tenant ID (e.g. "SRIT-ATP")
    tenant_id = Column(String(50), ForeignKey("identity_service.tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)

    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    department = Column(String(50), nullable=False, default="GENERAL")  # CSE, ECE, EEE, AIDS, etc.
    batch_year = Column(String(20), nullable=True)  # e.g. "2022-2026"

    # Custom Meaningful role_id (e.g. "ROLE_STUDENT", "ROLE_FACULTY")
    role_id = Column(String(50), ForeignKey("identity_service.roles.role_id", onupdate="CASCADE"), nullable=False)

    # Audit: User ID of the admin who provisioned this staff account (e.g. "ADM-SRIT-001")
    created_by_user_id = Column(String(100), ForeignKey("identity_service.users.user_id"), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    role = relationship("Role", foreign_keys=[role_id], lazy="joined")
    tenant = relationship("Tenant", foreign_keys=[tenant_id], lazy="joined")

    def __repr__(self):
        return f"<User user_id={self.user_id} tenant_id={self.tenant_id} role_id={self.role_id}>"
