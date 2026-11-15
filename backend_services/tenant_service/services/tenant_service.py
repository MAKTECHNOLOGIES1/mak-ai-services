"""
Tenant Business Logic Service
Handles college onboarding, module feature toggling, and stats aggregation.
Uses Supabase PostgREST via lightweight HTTP client.
"""

import logging
import uuid
from typing import Any, List, Optional

from core.database import SupabaseClient
from models.module_model import tenant_module_from_row
from models.tenant_model import tenant_from_row
from schemas.tenant_schemas import TenantCreate, TenantResponse, TenantStatsResponse, TenantUpdate

logger = logging.getLogger(__name__)

DEFAULT_MODULES = ["COLLEGE_AI", "FACULTY_AI", "PROJECT_STUDIO", "RAG_SYLLABUS"]


class TenantService:
    @staticmethod
    def _to_response(tenant: dict, enabled_modules: Optional[List[str]] = None) -> TenantResponse:
        modules = enabled_modules if enabled_modules is not None else []

        return TenantResponse(
            tenant_id=tenant["tenant_id"],
            name=tenant["name"],
            university_affiliation=tenant.get("university_affiliation", "JNTUA"),
            tier=tenant.get("tier", "STARTER"),
            max_students=tenant.get("max_students", 60),
            current_students=tenant.get("current_students", 0),
            max_faculty=tenant.get("max_faculty", 5),
            current_faculty=tenant.get("current_faculty", 0),
            monthly_ai_token_quota=tenant.get("monthly_ai_token_quota", 5000000),
            logo_url=tenant.get("logo_url"),
            contact_email=tenant.get("contact_email"),
            is_active=tenant.get("is_active", True),
            enabled_modules=modules,
            created_at=tenant.get("created_at"),
            updated_at=tenant.get("updated_at"),
        )

    @staticmethod
    async def get_tenant_by_id(db: SupabaseClient, tenant_id: str) -> Optional[TenantResponse]:
        row = await db.select("tenants", filters={"tenant_id": f"eq.{tenant_id}"}, single=True)
        if not row:
            return None
        tenant = tenant_from_row(row)

        # Fetch enabled modules
        mod_rows = await db.select(
            "tenant_modules",
            columns="module_key",
            filters={"tenant_id": f"eq.{tenant_id}", "is_enabled": "eq.true"},
        )
        modules = [m["module_key"] for m in (mod_rows or [])]
        return TenantService._to_response(tenant, modules)

    @staticmethod
    async def list_tenants(
        db: SupabaseClient,
        skip: int = 0,
        limit: int = 50,
    ) -> List[TenantResponse]:
        rows = await db.select(
            "tenants",
            order="created_at.desc",
            offset=skip,
            limit=limit,
        )
        results = []
        for row in (rows or []):
            tenant = tenant_from_row(row)
            results.append(TenantService._to_response(tenant))
        return results

    @staticmethod
    async def create_tenant(db: SupabaseClient, payload: TenantCreate) -> TenantResponse:
        # Check if already exists
        existing = await db.select("tenants", filters={"tenant_id": f"eq.{payload.tenant_id}"}, single=True)
        if existing:
            raise ValueError(f"Tenant with ID '{payload.tenant_id}' already exists.")

        new_row: dict[str, Any] = {
            "tenant_id": payload.tenant_id.strip().upper(),
            "name": payload.name.strip(),
            "university_affiliation": payload.university_affiliation.strip(),
            "tier": payload.tier.strip().upper(),
            "max_students": payload.max_students,
            "max_faculty": payload.max_faculty,
            "current_students": 0,
            "current_faculty": 0,
            "monthly_ai_token_quota": payload.monthly_ai_token_quota,
            "contact_email": str(payload.contact_email) if payload.contact_email else None,
            "logo_url": payload.logo_url,
            "is_active": True,
        }
        inserted = await db.insert("tenants", new_row)
        if not inserted:
            raise ValueError("Failed to insert tenant.")

        # Add initial modules
        modules_to_add = payload.enabled_modules or DEFAULT_MODULES
        for mod_key in modules_to_add:
            await db.insert("tenant_modules", {
                "id": str(uuid.uuid4()),
                "tenant_id": new_row["tenant_id"],
                "module_key": mod_key.strip().upper(),
                "is_enabled": True,
            })

        tenant = tenant_from_row(inserted)
        return TenantService._to_response(tenant, modules_to_add)

    @staticmethod
    async def update_tenant(
        db: SupabaseClient,
        tenant_id: str,
        payload: TenantUpdate,
    ) -> Optional[TenantResponse]:
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return await TenantService.get_tenant_by_id(db, tenant_id)

        # Normalize tier to uppercase
        if "tier" in update_data and update_data["tier"] is not None:
            update_data["tier"] = str(update_data["tier"]).upper()
        if "contact_email" in update_data and update_data["contact_email"] is not None:
            update_data["contact_email"] = str(update_data["contact_email"])

        # Remove None values
        clean_data = {k: v for k, v in update_data.items() if v is not None}

        updated = await db.update(
            "tenants",
            filters={"tenant_id": f"eq.{tenant_id}"},
            values=clean_data,
        )
        if not updated:
            return None

        tenant = tenant_from_row(updated)
        return TenantService._to_response(tenant)

    @staticmethod
    async def get_tenant_stats(db: SupabaseClient, tenant_id: str) -> Optional[TenantStatsResponse]:
        row = await db.select("tenants", filters={"tenant_id": f"eq.{tenant_id}"}, single=True)
        if not row:
            return None

        tenant = tenant_from_row(row)
        max_stu = tenant["max_students"]
        max_fac = tenant["max_faculty"]
        cur_stu = tenant["current_students"]
        cur_fac = tenant["current_faculty"]

        student_pct = round((cur_stu / max_stu) * 100, 1) if max_stu > 0 else 0.0
        faculty_pct = round((cur_fac / max_fac) * 100, 1) if max_fac > 0 else 0.0
        warning = student_pct >= 90.0 or faculty_pct >= 90.0

        return TenantStatsResponse(
            tenant_id=tenant["tenant_id"],
            name=tenant["name"],
            tier=tenant["tier"],
            student_seats_used=cur_stu,
            student_seats_max=max_stu,
            student_utilization_pct=student_pct,
            faculty_seats_used=cur_fac,
            faculty_seats_max=max_fac,
            faculty_utilization_pct=faculty_pct,
            is_capacity_warning=warning,
            monthly_ai_token_quota=tenant["monthly_ai_token_quota"],
            is_active=tenant["is_active"],
        )

    @staticmethod
    async def get_tenant_modules(db: SupabaseClient, tenant_id: str) -> List[str]:
        rows = await db.select(
            "tenant_modules",
            columns="module_key",
            filters={"tenant_id": f"eq.{tenant_id}", "is_enabled": "eq.true"},
        )
        return [m["module_key"] for m in (rows or [])]

    @staticmethod
    async def toggle_module(
        db: SupabaseClient,
        tenant_id: str,
        module_key: str,
        is_enabled: bool,
    ) -> List[str]:
        clean_key = module_key.strip().upper()

        # Check if module record exists
        existing = await db.select(
            "tenant_modules",
            filters={"tenant_id": f"eq.{tenant_id}", "module_key": f"eq.{clean_key}"},
            single=True,
        )

        if existing:
            await db.update(
                "tenant_modules",
                filters={"tenant_id": f"eq.{tenant_id}", "module_key": f"eq.{clean_key}"},
                values={"is_enabled": is_enabled},
            )
        else:
            await db.insert("tenant_modules", {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "module_key": clean_key,
                "is_enabled": is_enabled,
            })

        return await TenantService.get_tenant_modules(db, tenant_id)

    @staticmethod
    async def seed_default_tenant_if_missing(db: SupabaseClient):
        """Seeds default college SRIT-ATP if not present."""
        from core.config import settings
        default_id = settings.DEFAULT_TENANT_ID

        existing = await db.select("tenants", filters={"tenant_id": f"eq.{default_id}"}, single=True)
        if existing:
            return

        logger.info("Seeding default tenant %s via Supabase REST...", default_id)
        await db.insert("tenants", {
            "tenant_id": default_id,
            "name": "Srinivasa Ramanujan Institute of Technology",
            "university_affiliation": "JNTUA",
            "tier": "STARTER",
            "max_students": 60,
            "max_faculty": 5,
            "current_students": 0,
            "current_faculty": 0,
            "monthly_ai_token_quota": 5000000,
            "contact_email": "admin@srit.ac.in",
            "is_active": True,
        })

        for mod_key in DEFAULT_MODULES:
            await db.insert("tenant_modules", {
                "id": str(uuid.uuid4()),
                "tenant_id": default_id,
                "module_key": mod_key,
                "is_enabled": True,
            })
        logger.info("Default tenant %s seeded successfully.", default_id)
