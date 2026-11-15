"""
Role Model Helper for Identity Service
Provides row-to-dict conversion for Supabase PostgREST responses.
Pure Python — no SQLAlchemy dependency.
"""

from typing import Any


def role_from_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a PostgREST row dict into a normalized role dict."""
    perms = row.get("permissions")
    if perms is None:
        perms = []
    elif isinstance(perms, str):
        import json
        try:
            perms = json.loads(perms)
        except Exception:
            perms = [perms]

    return {
        "role_id": row.get("role_id"),
        "name": row.get("name"),
        "description": row.get("description"),
        "hierarchy_level": row.get("hierarchy_level", 10),
        "is_self_registerable": row.get("is_self_registerable", False),
        "is_active": row.get("is_active", True),
        "permissions": perms,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
