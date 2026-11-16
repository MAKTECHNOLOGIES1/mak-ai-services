"""
Supabase PostgREST Client for Identity Service
Uses Supabase PostgREST API via lightweight HTTP.
Compatible with Cloudflare Python Workers (Pyodide) and local development (httpx / urllib).
"""

import json
import logging
import os
from typing import Any, Optional

from core.config import settings

logger = logging.getLogger(__name__)


async def _fetch(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: str | None = None
) -> tuple[int, dict | list | None, str]:
    """
    Make an HTTP request.
    Priority: js.fetch (Cloudflare Workers) -> pyodide.http -> httpx / urllib (local dev).
    Returns (status_code, parsed_json_or_None, raw_text).
    """
    # 1. Try JavaScript fetch via Pyodide FFI (Cloudflare Workers runtime)
    try:
        from js import fetch as js_fetch, Object  # type: ignore[import-not-found]
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

    # 2. Try pyodide.http.pyfetch (Cloudflare Workers alternative)
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
        return int(resp.status), data, text
    except ImportError:
        pass

    # 3. Try httpx for local development
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.request(method, url, headers=headers, content=body)
            text = resp.text
            try:
                data = resp.json() if text else None
            except json.JSONDecodeError:
                data = None
            return resp.status_code, data, text
    except ImportError:
        pass

    # 4. Fallback to standard library urllib
    try:
        import asyncio
        import urllib.request
        import urllib.error

        def _sync_request():
            req_data = body.encode("utf-8") if body else None
            req = urllib.request.Request(url, data=req_data, headers=headers or {}, method=method)
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    raw = response.read().decode("utf-8")
                    code = response.getcode()
                    try:
                        parsed = json.loads(raw) if raw else None
                    except json.JSONDecodeError:
                        parsed = None
                    return code, parsed, raw
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8")
                try:
                    parsed = json.loads(raw) if raw else None
                except json.JSONDecodeError:
                    parsed = None
                return e.code, parsed, raw

        return await asyncio.to_thread(_sync_request)
    except Exception as e:
        logger.error("HTTP request error: %s", str(e))
        return 500, None, str(e)


class SupabaseClient:
    """Supabase PostgREST async client targeted at identity_service schema."""

    @property
    def base_url(self) -> str:
        url = os.getenv("SUPABASE_URL") or settings.SUPABASE_URL or "https://enkssiilvwiemxvsqaoy.supabase.co"
        return url.rstrip("/")

    @property
    def api_key(self) -> str:
        key = os.getenv("SUPABASE_SERVICE_KEY") or settings.SUPABASE_SERVICE_KEY
        if not key:
            try:
                from main import get_secret
                key = get_secret("SUPABASE_SERVICE_KEY")
            except Exception:
                pass
        return key or ""

    @property
    def schema(self) -> str:
        return os.getenv("DB_SCHEMA") or settings.DB_SCHEMA or "identity_service"

    def _headers(self, prefer: str = "return=representation") -> dict[str, str]:
        headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }
        # PostgREST schema headers
        if self.schema:
            headers["Accept-Profile"] = self.schema
            headers["Content-Profile"] = self.schema
        return headers

    def _rest_url(self, table: str) -> str:
        return f"{self.base_url}/rest/v1/{table}"

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        single: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        """
        Query rows from table.
        filters maps column to PostgREST operator expression, e.g.
        {"email": "eq.test@example.com", "is_active": "eq.true"}
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
            return None
        if status >= 400:
            logger.error("Supabase SELECT %s failed (%d): %s", table, status, text)
            return [] if not single else None
        return data

    async def insert(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]]
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Insert one or multiple rows into table."""
        url = self._rest_url(table)
        headers = self._headers(prefer="return=representation")
        body = json.dumps(data)

        status, res_data, text = await _fetch(url, "POST", headers, body=body)

        if status >= 400:
            logger.error("Supabase INSERT %s failed (%d): %s", table, status, text)
            raise ValueError(f"Supabase INSERT failed: {text}")

        if isinstance(data, dict) and isinstance(res_data, list) and len(res_data) > 0:
            return res_data[0]
        return res_data

    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, str]
    ) -> list[dict[str, Any]] | None:
        """Update rows matching filters."""
        if not filters:
            raise ValueError("Update requires filter criteria.")

        url = self._rest_url(table) + "?" + "&".join(f"{k}={v}" for k, v in filters.items())
        headers = self._headers(prefer="return=representation")
        body = json.dumps(data)

        status, res_data, text = await _fetch(url, "PATCH", headers, body=body)

        if status >= 400:
            logger.error("Supabase UPDATE %s failed (%d): %s", table, status, text)
            raise ValueError(f"Supabase UPDATE failed: {text}")
        return res_data

    async def delete(
        self,
        table: str,
        filters: dict[str, str]
    ) -> bool:
        """Delete rows matching filters."""
        if not filters:
            raise ValueError("Delete requires filter criteria.")

        url = self._rest_url(table) + "?" + "&".join(f"{k}={v}" for k, v in filters.items())
        headers = self._headers(prefer="return=representation")

        status, _, text = await _fetch(url, "DELETE", headers)
        if status >= 400:
            logger.error("Supabase DELETE %s failed (%d): %s", table, status, text)
            return False
        return True


supabase = SupabaseClient()

