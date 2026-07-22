from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleUserInfo(BaseModel):
    iss: str
    azp: str
    aud: str
    sub: str

    email: EmailStr
    email_verified: bool

    at_hash: str
    nonce: str

    name: str
    picture: str
    given_name: str
    family_name: str

    iat: int
    exp: int


class GoogleOAuthResponse(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    expires_at: int

    userinfo: GoogleUserInfo
