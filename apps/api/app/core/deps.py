from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from joserfc.errors import JoseError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User
from app.services.users import get_user_by_email

bearer_scheme = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter JWT Token",
    auto_error=False,
)

SessionDep = Annotated[AsyncSession, Depends(get_db)]
CredentialsDep = Annotated[
    HTTPAuthorizationCredentials, Depends(bearer_scheme)
]


async def get_current_user(
    session: SessionDep,
    credentials: CredentialsDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        claims = decode_access_token(settings, token)
    except JoseError:
        raise credentials_exception

    email = claims.get("sub")
    if email is None:
        raise credentials_exception

    user = await get_user_by_email(session, email)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.email_verified:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
