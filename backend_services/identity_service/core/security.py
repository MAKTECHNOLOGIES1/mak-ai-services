"""
Security Utilities: Password Hashing & JWT Token Generation
Supports both Passlib and native BCrypt for cross-version compatibility
"""

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import bcrypt
from core.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password Hashing context (BCrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a plaintext password using BCrypt"""
    clean_password = password.strip()
    try:
        return pwd_context.hash(clean_password)
    except (ValueError, TypeError, RuntimeError) as e:
        logger.debug("Passlib hash failed, falling back to direct bcrypt: %s", e)
        salt = bcrypt.gensalt(rounds=10)
        return bcrypt.hashpw(clean_password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored hash.
    Checks with and without whitespace, with passlib and native bcrypt.
    """
    clean_password = plain_password.strip()

    # 1. Try passlib verify
    try:
        if pwd_context.verify(clean_password, hashed_password):
            return True
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except (ValueError, TypeError, RuntimeError) as e:
        logger.debug("Passlib verify failed: %s", e)

    # 2. Try native bcrypt verify (handles $2a$, $2b$, and $2y$)
    try:
        encoded_hash = hashed_password.encode("utf-8")
        if bcrypt.checkpw(clean_password.encode("utf-8"), encoded_hash):
            return True
        if bcrypt.checkpw(plain_password.encode("utf-8"), encoded_hash):
            return True
    except (ValueError, TypeError, RuntimeError) as e:
        logger.debug("Direct bcrypt verify failed: %s", e)

    return False

def create_access_token(
    subject: str,
    tenant_id: str,
    role: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Generates a signed JWT access token containing tenant, user and role claims"""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "role": str(role),
        "exp": expire,
        "iat": now,
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodes and validates a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
