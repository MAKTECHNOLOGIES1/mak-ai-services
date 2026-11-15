"""
Tenant Module Schema
Tracks feature enablement (e.g. COLLEGE_AI, FACULTY_AI, PROJECT_STUDIO, RAG_SYLLABUS) per college.
Pure Python — no SQLAlchemy dependency.
"""


def tenant_module_from_row(row: dict) -> dict:
    """Convert a PostgREST row dict into a normalized module dict."""
    return {
        "id": row.get("id"),
        "tenant_id": row.get("tenant_id"),
        "module_key": row.get("module_key"),
        "is_enabled": row.get("is_enabled", True),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
