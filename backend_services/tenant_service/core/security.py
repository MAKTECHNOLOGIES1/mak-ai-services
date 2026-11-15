"""
Security Utilities for Tenant Service: JWT Token Decoding & Internal Service Verification
"""

import hmac
import logging
import secrets
from typing import Any, Optional
from jose import JWTError, jwt
from core.config import settings

logger = logging.getLogger(__name__)

def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decodes and validates a JWT token using HS256 secret.
    Returns the payload dictionary or None if expired or invalid.
    """
    clean_token = token.strip()
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()

    try:
        payload = jwt.decode(
            clean_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.debug("Tenant Service JWT decode error: %s", e)
        return None

def verify_internal_key(provided_key: Optional[str]) -> bool:
    """
    Validates inter-service communication key using constant-time comparison
    """
    if not provided_key or not settings.INTERNAL_SERVICE_KEY:
        return False
    return secrets.compare_digest(provided_key.strip(), settings.INTERNAL_SERVICE_KEY.strip())

