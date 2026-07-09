from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.deps import SessionDep
from app.core.security import create_access_token
from app.models import (
    Token,
    UserPasswordLoginRequestForm,
    UserPasswordSignupRequestForm,
)
from app.services.users import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup/password")
async def signup_password(
    session: SessionDep, form_data: UserPasswordSignupRequestForm
):
    user = await create_user(session, form_data)
    # TODO: also create the access token and add it to the response model
    return user


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    session: SessionDep, form_data: UserPasswordLoginRequestForm
) -> Token:
    user = authenticate_user(session, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        settings,
        data={"sub": form_data.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)
