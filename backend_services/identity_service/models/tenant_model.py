"""
Tenant Model Helper for Identity Service
Provides row-to-dict conversion for PostgREST responses.
Pure Python — no SQLAlchemy dependency.
"""

from typing import Any


def tenant_from_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a PostgREST row dict into a normalized tenant dict."""
    return {
        "tenant_id": row.get("tenant_id"),
        "name": row.get("name"),
        "university_affiliation": row.get("university_affiliation", "JNTUA"),
        "tier": row.get("tier", "STARTER"),
        "max_students": row.get("max_students", 60),
        "current_students": row.get("current_students", 0),
        "max_faculty": row.get("max_faculty", 5),
        "current_faculty": row.get("current_faculty", 0),
        "is_active": row.get("is_active", True),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
