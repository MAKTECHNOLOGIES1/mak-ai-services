"""
Seat Validator Service
Enforces strict seat caps (Starter: 60, Professional: 250, Enterprise: 600+)
Protects margins and multi-tenant quota boundaries
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.tenant_model import Tenant
from schemas.module_schemas import SeatCheckResponse

logger = logging.getLogger(__name__)

class SeatValidator:
    @staticmethod
    def _is_student_role(role_id: str) -> bool:
        r = role_id.upper()
        return r in ["ROLE_STUDENT", "STUDENT"]

    @staticmethod
    async def check_seat_availability(
        db: AsyncSession,
        tenant_id: str,
        role_id: str
    ) -> SeatCheckResponse:
        """
        Validates if the tenant has capacity to onboard a new student or faculty member
        """
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()

        if not tenant:
            return SeatCheckResponse(
                tenant_id=tenant_id,
                role_id=role_id,
                allowed=False,
                current_count=0,
                max_limit=0,
                remaining_seats=0,
                message=f"Tenant '{tenant_id}' does not exist."
            )

        if not tenant.is_active:
            return SeatCheckResponse(
                tenant_id=tenant_id,
                role_id=role_id,
                allowed=False,
                current_count=tenant.current_students,
                max_limit=tenant.max_students,
                remaining_seats=0,
                message=f"Tenant '{tenant_id}' account is deactivated."
            )

        if SeatValidator._is_student_role(role_id):
            current = tenant.current_students
            max_allowed = tenant.max_students
            remaining = max(0, max_allowed - current)
            allowed = current < max_allowed
            msg = "Student seat available." if allowed else f"Student seat cap reached ({current}/{max_allowed}). Please upgrade tier."
        else:
            # Faculty / Staff role
            current = tenant.current_faculty
            max_allowed = tenant.max_faculty
            remaining = max(0, max_allowed - current)
            allowed = current < max_allowed
            msg = "Faculty/Staff seat available." if allowed else f"Faculty seat cap reached ({current}/{max_allowed}). Please upgrade tier."

        return SeatCheckResponse(
            tenant_id=tenant_id,
            role_id=role_id,
            allowed=allowed,
            current_count=current,
            max_limit=max_allowed,
            remaining_seats=remaining,
            message=msg
        )

    @staticmethod
    async def increment_seat_count(
        db: AsyncSession,
        tenant_id: str,
        role_id: str,
        count: int = 1
    ) -> tuple[bool, int, int, str]:
        """
        Increments the seat count when a user registers or is provisioned.
        Returns: (success, current_students, current_faculty, message)
        """
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
        tenant = result.scalar_one_or_none()

        if not tenant:
            return False, 0, 0, f"Tenant '{tenant_id}' not found."

        if SeatValidator._is_student_role(role_id):
            if tenant.current_students + count > tenant.max_students:
                return False, tenant.current_students, tenant.current_faculty, "Student seat limit exceeded."
            tenant.current_students += count
        else:
            if tenant.current_faculty + count > tenant.max_faculty:
                return False, tenant.current_students, tenant.current_faculty, "Faculty seat limit exceeded."
            tenant.current_faculty += count

        await db.commit()
        await db.refresh(tenant)
        return True, tenant.current_students, tenant.current_faculty, "Seat successfully allocated."

    @staticmethod
    async def decrement_seat_count(
        db: AsyncSession,
        tenant_id: str,
        role_id: str,
        count: int = 1
    ) -> tuple[bool, int, int, str]:
        """
        Decrements the seat count when a user is de-provisioned.
        """
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id).with_for_update())
        tenant = result.scalar_one_or_none()

        if not tenant:
            return False, 0, 0, f"Tenant '{tenant_id}' not found."

        if SeatValidator._is_student_role(role_id):
            tenant.current_students = max(0, tenant.current_students - count)
        else:
            tenant.current_faculty = max(0, tenant.current_faculty - count)

        await db.commit()
        await db.refresh(tenant)
        return True, tenant.current_students, tenant.current_faculty, "Seat successfully released."

