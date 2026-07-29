from __future__ import annotations
import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status

ALGORITHM = "HS256"

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(subject: str, secret_key: str, expires_minutes: int = 15) -> str:
    """Create a short-lived JWT access token."""
    expire = _utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire, "jti": str(uuid.uuid4()), "type": "access"}
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)

def create_refresh_token(subject: str, secret_key: str, expires_days: int = 7) -> str:
    """Create a long-lived JWT refresh token."""
    expire = _utcnow() + timedelta(days=expires_days)
    payload = {"sub": subject, "exp": expire, "jti": str(uuid.uuid4()), "type": "refresh"}
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)

def decode_token(token: str, secret_key: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT token. Raises HTTPException on any error."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        token_type: str = payload.get("type", "")
        subject: str | None = payload.get("sub")
        if subject is None or token_type != expected_type:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
