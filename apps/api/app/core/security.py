from datetime import datetime, timedelta, timezone

import bcrypt
from joserfc import jwt
from joserfc.jwk import OctKey

from app.core.config import Settings

UTF_ENCODING = "utf-8"


def hash_password(password: str) -> str:
    password_bytes = password.encode(UTF_ENCODING)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode(UTF_ENCODING)


def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode(UTF_ENCODING)
    hashed_bytes = hashed_password.encode(UTF_ENCODING)
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    settings: Settings,
    data: dict,
    expires_delta: timedelta | None = None,
    auth_method: str = "password",
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire, "auth_method": auth_method})

    key = OctKey.import_key(settings.SECRET_KEY)
    header = {"alg": settings.ALGORITHM}
    return jwt.encode(header, to_encode, key)


def decode_access_token(settings: Settings, token: str) -> dict:
    key = OctKey.import_key(settings.SECRET_KEY)
    decoded = jwt.decode(token, key, algorithms=[settings.ALGORITHM])
    return decoded.claims
