"""
Tenant Model Helper
Provides row-to-dict conversion for PostgREST responses.
Pure Python — no SQLAlchemy dependency.
"""


def tenant_from_row(row: dict) -> dict:
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
        "monthly_ai_token_quota": row.get("monthly_ai_token_quota", 5000000),
        "logo_url": row.get("logo_url"),
        "contact_email": row.get("contact_email"),
        "is_active": row.get("is_active", True),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
