"""
JWT Verification & Context Extraction for API Gateway
"""

from typing import Optional, Dict, Any
from jose import jwt, JWTError
from core.config import settings

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates JWT token signature"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

