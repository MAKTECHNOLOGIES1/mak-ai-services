"""
Tenant Module Model
Tracks feature enablement (e.g. COLLEGE_AI, FACULTY_AI, PROJECT_STUDIO, RAG_SYLLABUS) per college
"""

from typing import ClassVar
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base

class TenantModule(Base):
    __tablename__ = "tenant_modules"
    __table_args__: ClassVar[tuple] = (
        UniqueConstraint("tenant_id", "module_key", name="uq_tenant_module"),
        {"schema": "identity_service"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        String(50),
        ForeignKey("identity_service.tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    module_key = Column(String(50), nullable=False) # e.g. "COLLEGE_AI", "FACULTY_AI", "PROJECT_STUDIO"
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tenant = relationship("Tenant", back_populates="modules")

    def __repr__(self):
        return f"<TenantModule tenant_id={self.tenant_id} module={self.module_key} enabled={self.is_enabled}>"

