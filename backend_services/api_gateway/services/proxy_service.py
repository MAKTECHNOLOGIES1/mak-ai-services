"""
Reverse Proxy Dispatcher for API Gateway:
Streams and proxies incoming API calls to downstream Cloudflare Workers microservices.
Propagates security context, tenant isolation headers, correlation IDs, and internal service keys.
Supports Cloudflare Workers (Pyodide js.fetch) and local development (httpx).
"""

import json
import logging
from typing import Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from core.config import settings

logger = logging.getLogger(__name__)

# Optional local dev HTTP client
_local_http_client = None


def get_local_http_client():
    global _local_http_client
    if _local_http_client is None:
        try:
            import httpx  # type: ignore[import-untyped]
            _local_http_client = httpx.AsyncClient(timeout=60.0)
        except ImportError:
            _local_http_client = None
    return _local_http_client


async def close_http_client():
    """Cleanup for local dev server shutdown"""
    global _local_http_client
    if _local_http_client is not None:
        try:
            await _local_http_client.aclose()
        except Exception:
            pass
        _local_http_client = None


async def proxy_to_service(
    request: Request,
    target_base_url: str,
    path: str
) -> Response:
    """
    Proxies an incoming request to the downstream microservice.
    Dual-mode: Uses Cloudflare js.fetch in Worker Pyodide runtime; httpx in local dev.
    """
    # 1. Build target URL
    target_base = target_base_url.rstrip("/")
    clean_path = path.lstrip("/")
    destination_url = f"{target_base}/{clean_path}"

    if request.url.query:
        destination_url = f"{destination_url}?{request.url.query}"

    # 2. Prepare headers to forward
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    headers.pop("connection", None)

    # Inject distributed tracing and security context headers
    correlation_id = getattr(request.state, "correlation_id", None)
    if correlation_id:
        headers["X-Correlation-ID"] = str(correlation_id)

    user_id = getattr(request.state, "user_id", None)
    if user_id:
        headers["X-User-Id"] = str(user_id)

    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id:
        headers["X-Tenant-Id"] = str(tenant_id)

    role = getattr(request.state, "role", None)
    if role:
        headers["X-Role-Id"] = str(role)

    # Forward internal service key for mutual microservice trust
    headers["X-Internal-Service-Key"] = settings.INTERNAL_SERVICE_KEY

    # 3. Read body content
    body_bytes = await request.body()
    body_payload: Optional[str] = None
    if body_bytes and request.method not in ["GET", "HEAD"]:
        try:
            body_payload = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            body_payload = str(body_bytes)

    # 4. Mode A: Cloudflare Workers Pyodide FFI (js.fetch)
    try:
        from js import fetch as js_fetch, Object, Uint8Array  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]

        opts: dict[str, Any] = {"method": request.method}
        if headers:
            opts["headers"] = to_js(headers, dict_converter=Object.fromEntries)
        if body_payload is not None:
            opts["body"] = body_payload

        js_resp = await js_fetch(destination_url, to_js(opts, dict_converter=Object.fromEntries))
        status_code = int(js_resp.status)

        # Extract response headers
        resp_headers: dict[str, str] = {}
        try:
            # Iterate JS Headers
            for pair in js_resp.headers.entries():
                k, v = pair[0], pair[1]
                if k.lower() not in ["content-encoding", "content-length", "transfer-encoding"]:
                    resp_headers[str(k)] = str(v)
        except Exception:
            pass

        if correlation_id:
            resp_headers["X-Correlation-ID"] = correlation_id

        # Extract body bytes via Uint8Array
        try:
            array_buf = await js_resp.arrayBuffer()
            content_bytes = bytes(Uint8Array.new(array_buf))
        except Exception:
            content_bytes = (await js_resp.text()).encode("utf-8")

        return Response(
            content=content_bytes,
            status_code=status_code,
            headers=resp_headers,
            media_type=resp_headers.get("content-type")
        )

    except ImportError:
        pass

    # 5. Mode B: pyodide.http.pyfetch (Workers alternate)
    try:
        from pyodide.http import pyfetch  # type: ignore[import-not-found]

        kwargs: dict[str, Any] = {"method": request.method, "headers": headers}
        if body_payload is not None:
            kwargs["body"] = body_payload

        py_resp = await pyfetch(destination_url, **kwargs)
        status_code = py_resp.status
        content_bytes = await py_resp.bytes()

        resp_headers = dict(py_resp.headers)
        resp_headers.pop("content-encoding", None)
        resp_headers.pop("content-length", None)
        resp_headers.pop("transfer-encoding", None)

        if correlation_id:
            resp_headers["X-Correlation-ID"] = correlation_id

        return Response(
            content=content_bytes,
            status_code=status_code,
            headers=resp_headers,
            media_type=resp_headers.get("content-type")
        )

    except ImportError:
        pass

    # 6. Mode C: Local Dev (httpx fallback)
    client = get_local_http_client()
    if client is not None:
        try:
            import httpx  # type: ignore[import-untyped]
            downstream_resp = await client.request(
                method=request.method,
                url=destination_url,
                headers=headers,
                content=body_bytes if body_bytes and request.method not in ["GET", "HEAD"] else None
            )

            resp_headers = dict(downstream_resp.headers)
            resp_headers.pop("content-encoding", None)
            resp_headers.pop("content-length", None)
            resp_headers.pop("transfer-encoding", None)

            if correlation_id:
                resp_headers["X-Correlation-ID"] = correlation_id

            return Response(
                content=downstream_resp.content,
                status_code=downstream_resp.status_code,
                headers=resp_headers,
                media_type=downstream_resp.headers.get("content-type")
            )
        except httpx.ConnectError:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": f"Downstream microservice at '{target_base_url}' is unreachable. Please verify the service is running."
                }
            )
        except httpx.TimeoutException:
            return JSONResponse(
                status_code=504,
                content={
                    "detail": f"Downstream microservice at '{target_base_url}' timed out processing the request."
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=502,
                content={
                    "detail": f"Gateway error forwarding request: {type(e).__name__}: {str(e)}"
                }
            )

    return JSONResponse(
        status_code=500,
        content={"detail": "No suitable HTTP dispatcher available in current runtime."}
    )
