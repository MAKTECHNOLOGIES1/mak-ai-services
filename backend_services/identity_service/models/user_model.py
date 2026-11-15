"""
User Model Helper for Identity Service
Provides row-to-dict conversion for Supabase PostgREST responses.
Pure Python — no SQLAlchemy dependency for Cloudflare Workers compatibility.
"""

from typing import Any


def user_from_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert a PostgREST row dict into a normalized user dict."""
    return {
        "user_id": row.get("user_id"),
        "tenant_id": row.get("tenant_id"),
        "email": row.get("email"),
        "password_hash": row.get("password_hash"),
        "full_name": row.get("full_name"),
        "department": row.get("department", "GENERAL"),
        "batch_year": row.get("batch_year"),
        "role_id": row.get("role_id", "ROLE_STUDENT"),
        "created_by_user_id": row.get("created_by_user_id"),
        "is_active": row.get("is_active", True),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
