"""
Dynamic Role Model
Uses meaningful role_id (e.g. 'ROLE_STUDENT', 'ROLE_FACULTY') as primary key
"""

from typing import ClassVar

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from core.database import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__: ClassVar[dict[str, str]] = {"schema": "identity_service"}

    # Meaningful custom role_id: e.g. "ROLE_STUDENT", "ROLE_FACULTY", "ROLE_HOD"
    role_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g. "Senior Technical Lead"
    description = Column(Text, nullable=True)
    hierarchy_level = Column(Integer, nullable=False, default=10)  # 1 to 100
    is_self_registerable = Column(Boolean, nullable=False, default=False)  # TRUE only for ROLE_STUDENT
    is_active = Column(Boolean, nullable=False, default=True)
    permissions = Column(JSONB, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Role role_id={self.role_id} name={self.name} level={self.hierarchy_level}>"
