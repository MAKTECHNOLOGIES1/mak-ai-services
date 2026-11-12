"""
Reverse Proxy Dispatcher:
Streams and proxies incoming API calls to downstream microservices.
Propagates headers, authentication context, and correlation IDs.
"""

import httpx
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from core.config import settings

# Global Async HTTP client pool for reverse proxying
http_client = httpx.AsyncClient(timeout=60.0)

async def proxy_to_service(
    request: Request,
    target_base_url: str,
    path: str
) -> Response:
    """
    Proxies an incoming request to the downstream microservice.
    """
    # 1. Build target URL
    # Clean trailing and leading slashes
    target_base_url = target_base_url.rstrip("/")
    clean_path = path.lstrip("/")
    destination_url = f"{target_base_url}/{clean_path}"

    if request.url.query:
        destination_url = f"{destination_url}?{request.url.query}"

    # 2. Prepare headers to forward
    headers = dict(request.headers)
    
    # Remove hop-by-hop headers
    headers.pop("host", None)
    headers.pop("content-length", None)

    # Inject distributed tracing and security context headers
    correlation_id = getattr(request.state, "correlation_id", None)
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    user_id = getattr(request.state, "user_id", None)
    if user_id:
        headers["X-User-Id"] = str(user_id)

    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id:
        headers["X-Tenant-Id"] = str(tenant_id)

    role = getattr(request.state, "role", None)
    if role:
        headers["X-Role-Id"] = str(role)

    # 3. Read body content
    body = await request.body()

    # 4. Dispatch async request to downstream service
    try:
        downstream_resp = await http_client.request(
            method=request.method,
            url=destination_url,
            headers=headers,
            content=body
        )

        # 5. Build response back to caller
        response_headers = dict(downstream_resp.headers)
        response_headers.pop("content-encoding", None)
        response_headers.pop("content-length", None)
        response_headers.pop("transfer-encoding", None)

        if correlation_id:
            response_headers["X-Correlation-ID"] = correlation_id

        return Response(
            content=downstream_resp.content,
            status_code=downstream_resp.status_code,
            headers=response_headers,
            media_type=downstream_resp.headers.get("content-type")
        )

    except httpx.ConnectError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": f"Downstream microservice at '{target_base_url}' is currently unreachable or offline. Please verify the service is running."
            }
        )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "detail": f"Downstream microservice at '{target_base_url}' timed out processing the request."
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "detail": f"Gateway error forwarding request: {type(e).__name__}: {str(e)}"
            }
        )

