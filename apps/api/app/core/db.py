from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlmodel import select

from app.core.config import settings
from app.core.security import hash_password

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    # Tables should be created with Alembic migrations.
    # If you don't want to use migrations, uncomment below:
    #
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from app.models import Account, User

        result = await session.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        )
        user = result.scalar_one_or_none()

        if not user:
            superuser = User(
                name=settings.FIRST_SUPERUSER_NAME,
                email=settings.FIRST_SUPERUSER,
                email_verified=True,
                is_super_user=True,
            )

            session.add(superuser)
            await session.commit()

            result = await session.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER)
            )

            superuser = result.scalar_one()
            superuser_creds = Account(
                provider_id="credential",
                account_id=superuser.id,
                user_id=superuser.id,
                password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            )

            session.add(superuser_creds)
            await session.commit()
