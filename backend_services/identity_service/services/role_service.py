"""
Dynamic Role Service: Manages custom, meaningful role_id
"""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.role_model import Role
from schemas.auth_schemas import RoleCreate

DEFAULT_ROLES = [
    {
        "role_id": "ROLE_SUPER_ADMIN",
        "name": "Super Administrator",
        "description": "AMK Platform Administrator with global platform authority",
        "hierarchy_level": 100,
        "is_self_registerable": False,
        "permissions": ["*"],
    },
    {
        "role_id": "ROLE_ADMIN",
        "name": "College Administrator",
        "description": "Institutional Admin (Principal / Management representative)",
        "hierarchy_level": 90,
        "is_self_registerable": False,
        "permissions": ["tenant:manage", "users:create", "naac:export", "reports:view"],
    },
    {
        "role_id": "ROLE_TECHNICAL_MANAGER",
        "name": "Technical Manager",
        "description": "Technical project manager overseeing engineering tracks",
        "hierarchy_level": 80,
        "is_self_registerable": False,
        "permissions": ["projects:manage", "curriculum:review", "reports:view"],
    },
    {
        "role_id": "ROLE_MANAGER",
        "name": "Innovation Manager",
        "description": "Manager coordinating departments and student outcomes",
        "hierarchy_level": 75,
        "is_self_registerable": False,
        "permissions": ["batches:manage", "reports:view"],
    },
    {
        "role_id": "ROLE_HOD",
        "name": "Head of Department",
        "description": "Department Head (CSE, ECE, EEE, etc.)",
        "hierarchy_level": 70,
        "is_self_registerable": False,
        "permissions": ["faculty:approve", "syllabus:manage", "reports:department"],
    },
    {
        "role_id": "ROLE_SR_LEAD",
        "name": "Senior Technical Lead",
        "description": "Senior Lead guiding student capstones and technical architecture",
        "hierarchy_level": 65,
        "is_self_registerable": False,
        "permissions": ["code:review", "projects:evaluate"],
    },
    {
        "role_id": "ROLE_TRAINER",
        "name": "Technical Trainer",
        "description": "Instructor delivering workshops, programming, and AI training",
        "hierarchy_level": 60,
        "is_self_registerable": False,
        "permissions": ["courses:teach", "attendance:mark", "assessments:grade"],
    },
    {
        "role_id": "ROLE_FACULTY",
        "name": "College Faculty / Professor",
        "description": "Teaching faculty preparing question papers and lesson plans",
        "hierarchy_level": 50,
        "is_self_registerable": False,
        "permissions": ["faculty_ai:use", "blooms:generate", "projects:review"],
    },
    {
        "role_id": "ROLE_TPO",
        "name": "Training & Placement Officer",
        "description": "Placement officer managing recruitment drives and internships",
        "hierarchy_level": 50,
        "is_self_registerable": False,
        "permissions": ["placements:manage", "internships:post", "portfolios:verify"],
    },
    {
        "role_id": "ROLE_STUDENT",
        "name": "Enrolled Student",
        "description": "College student (Roll Number is User ID)",
        "hierarchy_level": 10,
        "is_self_registerable": True,  # ONLY Student can self-register
        "permissions": ["chat:ask", "courses:learn", "projects:submit"],
    },
]


class RoleService:
    @staticmethod
    async def seed_default_roles_if_missing(db: AsyncSession):
        """Seeds standard roles on startup if table is empty"""
        for r in DEFAULT_ROLES:
            existing = await db.execute(select(Role).where(Role.role_id == r["role_id"]))
            if not existing.scalar_one_or_none():
                db.add(Role(**r))
        await db.commit()

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: str) -> Role | None:
        """Fetch role by its meaningful role_id (e.g. 'ROLE_STUDENT')"""
        clean_id = role_id.strip().upper()
        result = await db.execute(select(Role).where(Role.role_id == clean_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_roles(db: AsyncSession) -> list[Role]:
        result = await db.execute(select(Role).where(Role.is_active.is_(True)).order_by(Role.hierarchy_level.desc()))
        return list(result.scalars().all())

    @staticmethod
    async def create_dynamic_role(db: AsyncSession, role_in: RoleCreate) -> Role:
        """
        Allows administrators to create custom roles with custom or auto-generated role_id.
        Example: name="Dean Academics" -> role_id="ROLE_DEAN_ACADEMICS"
        """
        if role_in.role_id and role_in.role_id.strip():
            clean_role_id = role_in.role_id.strip().upper()
            if not clean_role_id.startswith("ROLE_"):
                clean_role_id = f"ROLE_{clean_role_id}"
        else:
            # Auto-generate from name: "Dean of Academics" -> "ROLE_DEAN_OF_ACADEMICS"
            slug = re.sub(r"[^A-Za-z0-9]+", "_", role_in.name).strip("_").upper()
            clean_role_id = f"ROLE_{slug}"

        existing = await RoleService.get_role_by_id(db, clean_role_id)
        if existing:
            raise ValueError(f"Role ID '{clean_role_id}' already exists")

        new_role = Role(
            role_id=clean_role_id,
            name=role_in.name,
            description=role_in.description,
            hierarchy_level=role_in.hierarchy_level,
            is_self_registerable=role_in.is_self_registerable,
            permissions=role_in.permissions,
        )
        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)
        return new_role
