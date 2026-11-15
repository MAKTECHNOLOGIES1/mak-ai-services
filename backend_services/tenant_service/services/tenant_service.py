"""
Tenant Business Logic Service
Handles college onboarding, module feature toggling, and stats aggregation
"""

import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.module_model import TenantModule
from models.tenant_model import Tenant
from schemas.tenant_schemas import TenantCreate, TenantResponse, TenantStatsResponse, TenantUpdate

logger = logging.getLogger(__name__)

DEFAULT_MODULES = ["COLLEGE_AI", "FACULTY_AI", "PROJECT_STUDIO", "RAG_SYLLABUS"]

class TenantService:
    @staticmethod
    def _to_response(tenant: Tenant, enabled_modules: Optional[List[str]] = None) -> TenantResponse:
        modules = enabled_modules
        if modules is None:
            if hasattr(tenant, "modules") and tenant.modules:
                modules = [m.module_key for m in tenant.modules if m.is_enabled]
            else:
                modules = []

        return TenantResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            university_affiliation=tenant.university_affiliation,
            tier=tenant.tier,
            max_students=tenant.max_students,
            current_students=tenant.current_students,
            max_faculty=tenant.max_faculty,
            current_faculty=tenant.current_faculty,
            monthly_ai_token_quota=tenant.monthly_ai_token_quota,
            logo_url=tenant.logo_url,
            contact_email=tenant.contact_email,
            is_active=tenant.is_active,
            enabled_modules=modules,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: str) -> Optional[TenantResponse]:
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None
        return TenantService._to_response(tenant)

    @staticmethod
    async def list_tenants(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[TenantResponse]:
        result = await db.execute(
            select(Tenant)
            .order_by(Tenant.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        tenants = result.scalars().all()
        return [TenantService._to_response(t) for t in tenants]

    @staticmethod
    async def create_tenant(db: AsyncSession, payload: TenantCreate) -> TenantResponse:
        # Check if already exists
        existing = await db.execute(select(Tenant).where(Tenant.tenant_id == payload.tenant_id))
        if existing.scalar_one_or_none():
            raise ValueError(f"Tenant with ID '{payload.tenant_id}' already exists.")

        new_tenant = Tenant(
            tenant_id=payload.tenant_id.strip().upper(),
            name=payload.name.strip(),
            university_affiliation=payload.university_affiliation.strip(),
            tier=payload.tier.strip().upper(),
            max_students=payload.max_students,
            max_faculty=payload.max_faculty,
            monthly_ai_token_quota=payload.monthly_ai_token_quota,
            contact_email=str(payload.contact_email) if payload.contact_email else None,
            logo_url=payload.logo_url,
            is_active=True
        )
        db.add(new_tenant)
        await db.flush()

        # Add initial modules
        modules_to_add = payload.enabled_modules or DEFAULT_MODULES
        for mod_key in modules_to_add:
            db.add(TenantModule(
                tenant_id=new_tenant.tenant_id,
                module_key=mod_key.strip().upper(),
                is_enabled=True
            ))

        await db.commit()
        await db.refresh(new_tenant)
        return TenantService._to_response(new_tenant, modules_to_add)

    @staticmethod
    async def update_tenant(
        db: AsyncSession,
        tenant_id: str,
        payload: TenantUpdate
    ) -> Optional[TenantResponse]:
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "tier" and value is not None:
                setattr(tenant, key, str(value).upper())
            elif key == "contact_email" and value is not None:
                setattr(tenant, key, str(value))
            elif value is not None:
                setattr(tenant, key, value)

        await db.commit()
        await db.refresh(tenant)
        return TenantService._to_response(tenant)

    @staticmethod
    async def get_tenant_stats(db: AsyncSession, tenant_id: str) -> Optional[TenantStatsResponse]:
        result = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return None

        student_pct = round((tenant.current_students / tenant.max_students) * 100, 1) if tenant.max_students > 0 else 0.0
        faculty_pct = round((tenant.current_faculty / tenant.max_faculty) * 100, 1) if tenant.max_faculty > 0 else 0.0
        warning = student_pct >= 90.0 or faculty_pct >= 90.0

        return TenantStatsResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            tier=tenant.tier,
            student_seats_used=tenant.current_students,
            student_seats_max=tenant.max_students,
            student_utilization_pct=student_pct,
            faculty_seats_used=tenant.current_faculty,
            faculty_seats_max=tenant.max_faculty,
            faculty_utilization_pct=faculty_pct,
            is_capacity_warning=warning,
            monthly_ai_token_quota=tenant.monthly_ai_token_quota,
            is_active=tenant.is_active
        )

    @staticmethod
    async def get_tenant_modules(db: AsyncSession, tenant_id: str) -> List[str]:
        result = await db.execute(
            select(TenantModule)
            .where(TenantModule.tenant_id == tenant_id, TenantModule.is_enabled == True)
        )
        return [m.module_key for m in result.scalars().all()]

    @staticmethod
    async def toggle_module(
        db: AsyncSession,
        tenant_id: str,
        module_key: str,
        is_enabled: bool
    ) -> List[str]:
        clean_key = module_key.strip().upper()
        result = await db.execute(
            select(TenantModule)
            .where(TenantModule.tenant_id == tenant_id, TenantModule.module_key == clean_key)
        )
        mod = result.scalar_one_or_none()

        if mod:
            mod.is_enabled = is_enabled
        else:
            db.add(TenantModule(
                tenant_id=tenant_id,
                module_key=clean_key,
                is_enabled=is_enabled
            ))

        await db.commit()
        return await TenantService.get_tenant_modules(db, tenant_id)

    @staticmethod
    async def seed_default_tenant_if_missing(db: AsyncSession):
        """Seeds default college SRIT-ATP if not present"""
        from core.config import settings
        default_id = settings.DEFAULT_TENANT_ID

        result = await db.execute(select(Tenant).where(Tenant.tenant_id == default_id))
        tenant = result.scalar_one_or_none()

        if not tenant:
            logger.info("Seeding default tenant %s into Supabase...", default_id)
            new_tenant = Tenant(
                tenant_id=default_id,
                name="Srinivasa Ramanujan Institute of Technology",
                university_affiliation="JNTUA",
                tier="STARTER",
                max_students=60,
                max_faculty=5,
                current_students=0,
                current_faculty=0,
                monthly_ai_token_quota=5000000,
                contact_email="admin@srit.ac.in",
                is_active=True
            )
            db.add(new_tenant)
            await db.flush()

            for mod_key in DEFAULT_MODULES:
                db.add(TenantModule(
                    tenant_id=default_id,
                    module_key=mod_key,
                    is_enabled=True
                ))
            await db.commit()
            logger.info("Default tenant %s seeded successfully.", default_id)

