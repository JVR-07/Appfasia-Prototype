from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
import bcrypt
from core.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_bytes = password.encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt).decode('ascii')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('ascii'))
    except ValueError:
        return False


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(tutor_id: str) -> str:
    return _create_token(
        {"sub": tutor_id, "type": "access"},
        timedelta(minutes=settings.jwt_access_expire_minutes),
    )


def create_refresh_token(tutor_id: str) -> str:
    return _create_token(
        {"sub": tutor_id, "type": "refresh"},
        timedelta(days=settings.jwt_refresh_expire_days),
    )


def decode_access_token(token: str) -> str:
    """Returns tutor_id or raises ValueError."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError("Not an access token")
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub claim")
        return sub
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e


def decode_refresh_token(token: str) -> str:
    """Returns tutor_id from refresh token or raises ValueError."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub claim")
        return sub
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
