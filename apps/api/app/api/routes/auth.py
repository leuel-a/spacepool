from datetime import timedelta

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from joserfc.errors import InvalidPayloadError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.config import Config

from app.core import config
from app.core.config import settings
from app.core.deps import SessionDep
from app.core.security import create_access_token
from app.models import (
    GoogleOAuthResponse,
    Token,
    User,
)
from app.models.user import (
    UserPasswordLoginRequestForm,
    UserPasswordSignupRequestForm,
    UserPasswordSignupResponse,
)
from app.services.users import (
    authenticate_user,
    create_user_password,
    create_user_provider,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ENV_PATH = ".env"

config = Config(ENV_PATH)
oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/signup/password", response_model=UserPasswordSignupResponse)
async def signup_password(
    session: SessionDep, form_data: UserPasswordSignupRequestForm
):
    try:
        user_input = User(
            name=form_data.name,
            email=form_data.email,
            email_verified=False,
            is_super_user=False,
        )
        user = await create_user_password(
            session, user_input, form_data.password
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    try:
        access_token = create_access_token(
            settings,
            data={"sub": user.email},
            expires_delta=access_token_expires,
        )
    except (ValueError, InvalidPayloadError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong please try again",
        )

    return UserPasswordSignupResponse(
        name=user.name, email=user.email, token=Token(access_token=access_token)
    )


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

    try:
        access_token = create_access_token(
            settings,
            data={"sub": form_data.email},
            expires_delta=access_token_expires,
        )
    except (ValueError, InvalidPayloadError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong please try again",
        )
    return Token(access_token=access_token)


@router.get("/google")
async def google(request: Request):
    redirect_url = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_url)  # type: ignore


@router.get("/google/callback", response_model=Token)
async def google_callback(session: SessionDep, request: Request):
    raw_token = await oauth.google.authorize_access_token(request)  # type: ignore

    try:
        token = GoogleOAuthResponse.model_validate(raw_token)
        user = await create_user_provider(session, token)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while trying to get google credentials",
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    try:
        access_token = create_access_token(
            settings,
            data={"sub": user.email},
            expires_delta=access_token_expires,
        )
    except (ValueError, InvalidPayloadError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong please try again",
        )
    return Token(access_token=access_token)
