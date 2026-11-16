"""
Security and Cryptography utilities for Identity Service
Provides JWT access/refresh token creation, validation, and password hashing/verification.
Zero external C-extension dependencies required — natively compatible with Pyodide / Cloudflare Workers.
All secrets loaded strictly from environment / Cloudflare Secrets via config.
"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from core.config import settings


# ── Password Hashing & Verification ──────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with a unique random salt.
    Compatible across all Python environments including Cloudflare Workers.
    Output format: pbkdf2:sha256:100000$<salt_hex>$<hash_hex>
    """
    salt = os.urandom(16)
    iterations = 100000
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2:sha256:{iterations}${salt.hex()}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a stored hash.
    Supports PBKDF2-SHA256 and BCrypt (if bcrypt package is present).
    """
    if not plain_password or not hashed_password:
        return False

    # 1. PBKDF2 format
    if hashed_password.startswith("pbkdf2:sha256:"):
        try:
            parts = hashed_password.split("$")
            header = parts[0]
            salt_hex = parts[1]
            stored_hash_hex = parts[2]
            iterations = int(header.split(":")[2])

            salt = bytes.fromhex(salt_hex)
            test_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(test_hash.hex(), stored_hash_hex)
        except Exception:
            return False

    # 2. BCrypt format (e.g. from seed SQL $2a$ or $2b$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ImportError:
            pass

    # 3. Direct compare fallback for development/testing
    if plain_password == hashed_password:
        return True

    return False


# ── JWT Token Operations ─────────────────────────────────────────────────────

def _get_jwt_secret() -> str:
    """Ensure JWT_SECRET is configured in environment / Cloudflare Secrets."""
    secret = settings.JWT_SECRET
    if not secret:
        raise ValueError("JWT_SECRET is not configured in .env or Cloudflare Worker Secrets.")
    return secret


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT Access Token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "token_type": "access"
    })

    secret = _get_jwt_secret()
    return jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT Refresh Token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "token_type": "refresh"
    })

    secret = _get_jwt_secret()
    return jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if invalid or expired.
    """
    secret = _get_jwt_secret()
    return jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
