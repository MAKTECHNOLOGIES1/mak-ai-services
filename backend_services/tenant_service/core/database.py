"""
Supabase REST Client for Tenant Service
Uses Supabase PostgREST API via lightweight HTTP — compatible with Cloudflare Python Workers (Pyodide).
Replaces SQLAlchemy which exceeds the 128 MB startup memory limit on Workers.
"""

import json
import logging
from typing import Any, Optional

from core.config import settings

logger = logging.getLogger(__name__)

# ── Lightweight HTTP helper (works in both Pyodide/Workers and local Python) ──


async def _fetch(url: str, method: str = "GET", headers: dict | None = None,
                 body: str | None = None) -> tuple[int, dict | list | None, str]:
    """
    Make an HTTP request.
    Priority: js.fetch (Cloudflare Workers) → pyodide.http → httpx (local dev).
    Returns (status_code, parsed_json_or_None, raw_text).
    """
    # 1. Try JavaScript fetch via Pyodide FFI (Cloudflare Workers runtime)
    try:
        from js import fetch as js_fetch, Object, Headers as JsHeaders  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]

        opts: dict[str, Any] = {"method": method}
        if headers:
            opts["headers"] = to_js(headers, dict_converter=Object.fromEntries)
        if body:
            opts["body"] = body

        resp = await js_fetch(url, to_js(opts, dict_converter=Object.fromEntries))
        text = str(await resp.text())
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = None
        return int(resp.status), data, text
    except ImportError:
        pass

    # 2. Try pyodide.http.pyfetch (also Cloudflare Workers, slightly higher level)
    try:
        from pyodide.http import pyfetch  # type: ignore[import-not-found]
        kwargs: dict[str, Any] = {"method": method}
        if headers:
            kwargs["headers"] = headers
        if body:
            kwargs["body"] = body
        resp = await pyfetch(url, **kwargs)
        text = await resp.string()
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = None
        return resp.status, data, text
    except ImportError:
        pass

    # 3. Local dev fallback – httpx
    try:
        import httpx  # type: ignore[import-untyped]
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method, url, headers=headers, content=body)
            text = resp.text
            try:
                data = resp.json() if text else None
            except Exception:
                data = None
            return resp.status_code, data, text
    except ImportError:
        raise RuntimeError(
            "No HTTP client available. Install 'httpx' for local dev, "
            "or ensure js/pyodide modules are available in Cloudflare Workers."
        )


class SupabaseClient:
    """
    Minimal Supabase PostgREST client for CRUD on tables in a specific schema.
    """

    def __init__(
        self,
        supabase_url: str = "",
        supabase_key: str = "",
        schema: str = "public"
    ):
        self.base_url = supabase_url.rstrip("/")
        self.key = supabase_key
        self.schema = schema

    def _headers(self, *, prefer: str = "") -> dict[str, str]:
        h: dict[str, str] = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Accept-Profile": self.schema,
            "Content-Profile": self.schema,
        }
        if prefer:
            h["Prefer"] = prefer
        return h

    def _rest_url(self, table: str) -> str:
        return f"{self.base_url}/rest/v1/{table}"

    # ── SELECT ───────────────────────────────────────────────────────────────

    async def select(
        self,
        table: str,
        *,
        columns: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        single: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        """
        SELECT rows from a table via PostgREST.
        `filters` maps column names to PostgREST filter expressions,
        e.g. {"tenant_id": "eq.SRIT-ATP", "is_enabled": "eq.true"}
        """
        url = f"{self._rest_url(table)}?select={columns}"
        if filters:
            for col, expr in filters.items():
                url += f"&{col}={expr}"
        if order:
            url += f"&order={order}"
        if limit is not None:
            url += f"&limit={limit}"
        if offset is not None:
            url += f"&offset={offset}"

        prefer = "return=representation"
        if single:
            prefer += ",count=exact"
        headers = self._headers(prefer=prefer)
        if single:
            headers["Accept"] = "application/vnd.pgrst.object+json"

        status, data, text = await _fetch(url, "GET", headers)

        if status == 406 and single:
            # No row found
            return None
        if status >= 400:
            logger.error("Supabase SELECT %s failed (%d): %s", table, status, text)
            return [] if not single else None
        return data

    # ── INSERT ───────────────────────────────────────────────────────────────

    async def insert(
        self, table: str, row: dict[str, Any]
    ) -> dict[str, Any] | None:
        url = self._rest_url(table)
        headers = self._headers(prefer="return=representation")
        headers["Accept"] = "application/vnd.pgrst.object+json"

        status, data, text = await _fetch(url, "POST", headers, json.dumps(row, default=str))

        if status == 409:
            raise ValueError(f"Duplicate row in {table}: {text}")
        if status >= 400:
            logger.error("Supabase INSERT %s failed (%d): %s", table, status, text)
            return None
        return data  # type: ignore[return-value]

    # ── UPDATE (PATCH) ───────────────────────────────────────────────────────

    async def update(
        self,
        table: str,
        filters: dict[str, str],
        values: dict[str, Any],
    ) -> dict[str, Any] | None:
        url = self._rest_url(table)
        for col, expr in filters.items():
            url += f"&{col}={expr}" if "?" in url else f"?{col}={expr}"

        headers = self._headers(prefer="return=representation")
        headers["Accept"] = "application/vnd.pgrst.object+json"

        status, data, text = await _fetch(url, "PATCH", headers, json.dumps(values, default=str))

        if status == 406:
            return None
        if status >= 400:
            logger.error("Supabase UPDATE %s failed (%d): %s", table, status, text)
            return None
        return data  # type: ignore[return-value]

    # ── RPC (for transactional operations like seat increment) ────────────

    async def rpc(
        self, function_name: str, params: dict[str, Any]
    ) -> dict[str, Any] | list | None:
        url = f"{self.base_url}/rest/v1/rpc/{function_name}"
        headers = self._headers(prefer="return=representation")

        status, data, text = await _fetch(url, "POST", headers, json.dumps(params, default=str))
        if status >= 400:
            logger.error("Supabase RPC %s failed (%d): %s", function_name, status, text)
            return None
        return data

    # ── DELETE ────────────────────────────────────────────────────────────────

    async def delete(self, table: str, filters: dict[str, str]) -> bool:
        url = self._rest_url(table)
        for col, expr in filters.items():
            url += f"&{col}={expr}" if "?" in url else f"?{col}={expr}"

        status, _, text = await _fetch(url, "DELETE", self._headers())
        if status >= 400:
            logger.error("Supabase DELETE %s failed (%d): %s", table, status, text)
            return False
        return True


# ── Lazy Client Access ────────────────────────────────────────────────────────

_db_client: Optional[SupabaseClient] = None


def get_db_client() -> Optional[SupabaseClient]:
    """Returns singleton Supabase client, initialized lazily."""
    global _db_client
    if _db_client is None:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            _db_client = SupabaseClient(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SERVICE_KEY,
                schema=settings.DB_SCHEMA,
            )
        else:
            logger.warning(
                "SUPABASE_URL or SUPABASE_SERVICE_KEY not set — database operations will be unavailable."
            )
    return _db_client


async def get_db() -> Optional[SupabaseClient]:
    """FastAPI dependency — returns the Supabase REST client."""
    return get_db_client()
