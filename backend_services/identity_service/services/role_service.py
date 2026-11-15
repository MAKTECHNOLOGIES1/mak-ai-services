"""
Dynamic Role Service for Identity Service
Manages custom, meaningful role_id values via Supabase PostgREST
"""

import logging
import re
from typing import Any, Optional

from core.database import SupabaseClient
from models.role_model import role_from_row
from schemas.auth_schemas import RoleCreate, RoleResponse

logger = logging.getLogger(__name__)

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
    async def seed_default_roles_if_missing(db: SupabaseClient):
        """Seeds standard roles on startup if table is empty or missing defaults"""
        for r in DEFAULT_ROLES:
            existing = await db.select("roles", filters={"role_id": f"eq.{r['role_id']}"}, single=True)
            if not existing:
                try:
                    await db.insert("roles", {
                        "role_id": r["role_id"],
                        "name": r["name"],
                        "description": r["description"],
                        "hierarchy_level": r["hierarchy_level"],
                        "is_self_registerable": r["is_self_registerable"],
                        "is_active": True,
                        "permissions": r["permissions"],
                    })
                    logger.info("Seeded default role: %s", r["role_id"])
                except Exception as e:
                    logger.warning("Could not seed role %s: %s", r["role_id"], e)

    @staticmethod
    async def get_role_by_id(db: SupabaseClient, role_id: str) -> Optional[dict[str, Any]]:
        clean_role_id = role_id.strip().upper()
        if not clean_role_id.startswith("ROLE_"):
            clean_role_id = f"ROLE_{clean_role_id}"

        row = await db.select("roles", filters={"role_id": f"eq.{clean_role_id}"}, single=True)
        if not row:
            # Check without ROLE_ prefix as fallback
            alt_id = clean_role_id.replace("ROLE_", "", 1)
            row = await db.select("roles", filters={"role_id": f"eq.{alt_id}"}, single=True)
        return role_from_row(row) if row else None

    @staticmethod
    async def get_all_roles(db: SupabaseClient) -> list[RoleResponse]:
        rows = await db.select("roles", order="hierarchy_level.desc")
        results: list[RoleResponse] = []
        for r in (rows or []):
            role_dict = role_from_row(r)
            results.append(RoleResponse(**role_dict))
        return results

    @staticmethod
    async def create_dynamic_role(db: SupabaseClient, payload: RoleCreate) -> RoleResponse:
        if payload.role_id:
            clean_role_id = payload.role_id.strip().upper()
            if not clean_role_id.startswith("ROLE_"):
                clean_role_id = f"ROLE_{clean_role_id}"
        else:
            slug = re.sub(r"[^A-Za-z0-9]+", "_", payload.name.strip().upper()).strip("_")
            clean_role_id = f"ROLE_{slug}"

        existing = await db.select("roles", filters={"role_id": f"eq.{clean_role_id}"}, single=True)
        if existing:
            raise ValueError(f"Role ID '{clean_role_id}' already exists.")

        new_row = {
            "role_id": clean_role_id,
            "name": payload.name.strip(),
            "description": payload.description,
            "hierarchy_level": payload.hierarchy_level,
            "is_self_registerable": payload.is_self_registerable,
            "is_active": True,
            "permissions": payload.permissions,
        }

        inserted = await db.insert("roles", new_row)
        if not inserted:
            raise ValueError(f"Failed to create role '{clean_role_id}'.")

        role_dict = role_from_row(inserted)
        return RoleResponse(**role_dict)
