from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.main import api_router
from app.core.config import settings

app = FastAPI(
    name=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(api_router, prefix=settings.API_V1_STR)
