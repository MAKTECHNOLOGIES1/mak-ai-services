"""
API Gateway Middlewares:
1. Correlation ID tracking (X-Correlation-ID)
2. In-memory Rate Limiting per IP
3. Pre-Authentication & Context Injection
"""

import time
import uuid
from typing import Dict, List
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings
from core.security import decode_token

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Ensures every request has a unique correlation ID for distributed tracing"""
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window in-memory rate limiter per Client IP.
    Default: 60 requests/minute to prevent abuse.
    """
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.clients: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check and docs
        path = request.url.path
        if path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - 60.0

        timestamps = self.clients.get(client_ip, [])
        # Filter timestamps within current 60s window
        timestamps = [t for t in timestamps if t > window_start]
        
        if len(timestamps) >= self.rpm:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded: {self.rpm} requests per minute limit. Please try again shortly."
                },
                headers={"Retry-After": "60"}
            )

        timestamps.append(now)
        self.clients[client_ip] = timestamps
        return await call_next(request)

class AuthPreValidationMiddleware(BaseHTTPMiddleware):
    """
    Inspects incoming requests:
    - Bypasses public endpoints (login, register, health, docs)
    - Validates Bearer token for protected routes
    - Injects user claims into request.state for downstream propagation
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 1. Bypass public paths
        for public_path in settings.PUBLIC_PATHS:
            if path == public_path or path.startswith(public_path + "/"):
                return await call_next(request)

        # 2. Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header. Expected 'Bearer <token>'"}
            )

        token = auth_header.split(" ", 1)[1].strip()

        # 3. Decode & Verify JWT
        payload = decode_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token is invalid, expired, or signature verification failed."}
            )

        # 4. Attach claims to request.state
        request.state.user_id = payload.get("sub")
        request.state.tenant_id = payload.get("tenant_id")
        request.state.role = payload.get("role")
        request.state.email = payload.get("email")
        request.state.department = payload.get("department")

        return await call_next(request)

