from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context using bcrypt.
password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    """
    return password_context.verify(plain_password, password_hash)


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    """
    Create a JWT access token.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )