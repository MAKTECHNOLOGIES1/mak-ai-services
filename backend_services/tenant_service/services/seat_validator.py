"""
Seat Validator Service
Enforces strict seat caps (Starter: 60, Professional: 250, Enterprise: 600+)
Protects margins and multi-tenant quota boundaries.
Uses Supabase PostgREST via lightweight HTTP.
"""

import logging
from typing import Any

from core.database import SupabaseClient
from models.tenant_model import tenant_from_row
from schemas.module_schemas import SeatCheckResponse

logger = logging.getLogger(__name__)


class SeatValidator:
    @staticmethod
    def _is_student_role(role_id: str) -> bool:
        r = role_id.upper()
        return r in ["ROLE_STUDENT", "STUDENT"]

    @staticmethod
    async def check_seat_availability(
        db: SupabaseClient,
        tenant_id: str,
        role_id: str,
    ) -> SeatCheckResponse:
        """
        Validates if the tenant has capacity to onboard a new student or faculty member.
        """
        row = await db.select("tenants", filters={"tenant_id": f"eq.{tenant_id}"}, single=True)

        if not row:
            return SeatCheckResponse(
                tenant_id=tenant_id,
                role_id=role_id,
                allowed=False,
                current_count=0,
                max_limit=0,
                remaining_seats=0,
                message=f"Tenant '{tenant_id}' does not exist.",
            )

        tenant = tenant_from_row(row)

        if not tenant["is_active"]:
            return SeatCheckResponse(
                tenant_id=tenant_id,
                role_id=role_id,
                allowed=False,
                current_count=tenant["current_students"],
                max_limit=tenant["max_students"],
                remaining_seats=0,
                message=f"Tenant '{tenant_id}' account is deactivated.",
            )

        if SeatValidator._is_student_role(role_id):
            current = tenant["current_students"]
            max_allowed = tenant["max_students"]
            remaining = max(0, max_allowed - current)
            allowed = current < max_allowed
            msg = (
                "Student seat available."
                if allowed
                else f"Student seat cap reached ({current}/{max_allowed}). Please upgrade tier."
            )
        else:
            current = tenant["current_faculty"]
            max_allowed = tenant["max_faculty"]
            remaining = max(0, max_allowed - current)
            allowed = current < max_allowed
            msg = (
                "Faculty/Staff seat available."
                if allowed
                else f"Faculty seat cap reached ({current}/{max_allowed}). Please upgrade tier."
            )

        return SeatCheckResponse(
            tenant_id=tenant_id,
            role_id=role_id,
            allowed=allowed,
            current_count=current,
            max_limit=max_allowed,
            remaining_seats=remaining,
            message=msg,
        )

    @staticmethod
    async def increment_seat_count(
        db: SupabaseClient,
        tenant_id: str,
        role_id: str,
        count: int = 1,
    ) -> tuple[bool, int, int, str]:
        """
        Increments the seat count when a user registers or is provisioned.
        Returns: (success, current_students, current_faculty, message)
        """
        row = await db.select("tenants", filters={"tenant_id": f"eq.{tenant_id}"}, single=True)

        if not row:
            return False, 0, 0, f"Tenant '{tenant_id}' not found."

        tenant = tenant_from_row(row)
        update_data: dict[str, Any] = {}

        if SeatValidator._is_student_role(role_id):
            new_count = tenant["current_students"] + count
            if new_count > tenant["max_students"]:
                return (
                    False,
                    tenant["current_students"],
                    tenant["current_faculty"],
                    "Student seat limit exceeded.",
                )
            update_data["current_students"] = new_count
        else:
            new_count = tenant["current_faculty"] + count
            if new_count > tenant["max_faculty"]:
                return (
                    False,
                    tenant["current_students"],
                    tenant["current_faculty"],
                    "Faculty seat limit exceeded.",
                )
            update_data["current_faculty"] = new_count

        updated = await db.update(
            "tenants",
            filters={"tenant_id": f"eq.{tenant_id}"},
            values=update_data,
        )
        if updated:
            t = tenant_from_row(updated)
            return True, t["current_students"], t["current_faculty"], "Seat successfully allocated."
        return False, tenant["current_students"], tenant["current_faculty"], "Failed to update seat count."

    @staticmethod
    async def decrement_seat_count(
        db: SupabaseClient,
        tenant_id: str,
        role_id: str,
        count: int = 1,
    ) -> tuple[bool, int, int, str]:
        """
        Decrements the seat count when a user is de-provisioned.
        """
        row = await db.select("tenants", filters={"tenant_id": f"eq.{tenant_id}"}, single=True)

        if not row:
            return False, 0, 0, f"Tenant '{tenant_id}' not found."

        tenant = tenant_from_row(row)
        update_data: dict[str, Any] = {}

        if SeatValidator._is_student_role(role_id):
            update_data["current_students"] = max(0, tenant["current_students"] - count)
        else:
            update_data["current_faculty"] = max(0, tenant["current_faculty"] - count)

        updated = await db.update(
            "tenants",
            filters={"tenant_id": f"eq.{tenant_id}"},
            values=update_data,
        )
        if updated:
            t = tenant_from_row(updated)
            return True, t["current_students"], t["current_faculty"], "Seat successfully released."
        return False, tenant["current_students"], tenant["current_faculty"], "Failed to update seat count."
