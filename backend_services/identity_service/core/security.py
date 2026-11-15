"""
Security Utilities: Password Hashing, JWT Generation, and Inter-Service Keys
Cloudflare Python Workers (Pyodide) compatible with pure-Python PBKDF2 and BCrypt support
"""

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import logging
import secrets
from typing import Any

from core.config import settings
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# Try optional bcrypt import if available in runtime
try:
    import bcrypt  # type: ignore[import-not-found]
except ImportError:
    bcrypt = None


def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 (safe for Cloudflare Pyodide / WebAssembly)
    or bcrypt if native library is available.
    """
    clean_password = password.strip()

    # If bcrypt is available, prefer bcrypt
    if bcrypt is not None:
        try:
            salt = bcrypt.gensalt(rounds=10)
            return bcrypt.hashpw(clean_password.encode("utf-8"), salt).decode("utf-8")
        except Exception as e:
            logger.debug("Bcrypt hashing failed, falling back to PBKDF2: %s", e)

    # Pure Python PBKDF2-HMAC-SHA256 fallback (universal and secure)
    salt_hex = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        clean_password.encode("utf-8"),
        salt_hex.encode("utf-8"),
        100000
    )
    return f"pbkdf2:sha256:100000${salt_hex}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored hash.
    Supports PBKDF2 and BCrypt hashes ($2a$, $2b$, $2y$).
    """
    clean_password = plain_password.strip()

    # 1. PBKDF2 format check
    if hashed_password.startswith("pbkdf2:sha256:"):
        try:
            parts = hashed_password.split("$")
            if len(parts) == 3:
                rounds = int(parts[0].split(":")[-1])
                salt_hex = parts[1]
                stored_hash = parts[2]
                computed = hashlib.pbkdf2_hmac(
                    "sha256",
                    clean_password.encode("utf-8"),
                    salt_hex.encode("utf-8"),
                    rounds
                ).hex()
                return hmac.compare_digest(computed, stored_hash)
        except Exception as e:
            logger.debug("PBKDF2 verification failed: %s", e)

    # 2. BCrypt format check ($2a$, $2b$, $2y$)
    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        if bcrypt is not None:
            try:
                encoded_hash = hashed_password.encode("utf-8")
                if bcrypt.checkpw(clean_password.encode("utf-8"), encoded_hash):
                    return True
                if bcrypt.checkpw(plain_password.encode("utf-8"), encoded_hash):
                    return True
            except Exception as e:
                logger.debug("Bcrypt verification error: %s", e)

    # 3. Direct compare for testing/seed accounts (only if plain text matches)
    if hmac.compare_digest(plain_password, hashed_password):
        return True

    return False


def create_access_token(
    subject: str,
    tenant_id: str,
    role: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generates a signed JWT access token containing standard identity claims.
    Ensures sub, user_id, tenant_id, role, and role_id are all populated for
    seamless interoperability across tenant_service, api_gateway, and UI.
    """
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    clean_role = role.upper() if role.upper().startswith("ROLE_") else f"ROLE_{role.upper()}"

    to_encode = {
        "sub": str(subject),
        "user_id": str(subject),
        "tenant_id": str(tenant_id),
        "role": clean_role,
        "role_id": clean_role,
        "exp": expire,
        "iat": now,
    }

    if extra_claims:
        to_encode.update(extra_claims)

    if not settings.JWT_SECRET:
        logger.error("JWT_SECRET is missing. Please set JWT_SECRET in .env or Cloudflare Worker secrets.")
        raise ValueError("JWT_SECRET is not configured.")

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodes and validates a JWT token"""
    if not settings.JWT_SECRET:
        logger.error("JWT_SECRET is missing. Cannot decode access token.")
        return None
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def verify_internal_key(provided_key: str | None) -> bool:
    """Validates secret key for trusted microservice-to-microservice calls"""
    if not provided_key or not settings.INTERNAL_SERVICE_KEY:
        return False
    return hmac.compare_digest(provided_key.strip(), settings.INTERNAL_SERVICE_KEY.strip())
