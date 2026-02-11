import jwt
import uuid

from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from agent.core.config import settings

password_hash = PasswordHash.recommended()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password."""
    return password_hash.verify(password=plain, hash=hashed)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return password_hash.hash(password=password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def is_token_expired(expiration) -> bool:
    return datetime.now(timezone.utc) >= datetime.fromtimestamp(
        expiration, timezone.utc
    )
