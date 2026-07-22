import uuid

from pydantic import BaseModel
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.shared import TimestampMixin, Token


class UserPasswordSignupRequestForm(BaseModel):
    name: str
    email: str
    password: str


class UserPasswordLoginRequestForm(BaseModel):
    email: str
    password: str


class UserPasswordSignupResponse(BaseModel):
    name: str
    email: str
    token: Token


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_super_user: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    organization: Mapped["Organization"] = relationship( # type: ignore
        back_populates="owner",
        uselist=False
    )
    accounts: Mapped[list["Account"]] = relationship( # type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
