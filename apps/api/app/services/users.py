from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument

from app.core.security import hash_password, verify_password
from app.models import Account, User, UserPasswordSignupRequestForm


async def get_user(
    db: AsyncSession, whereclause: ColumnExpressionArgument[bool]
):
    stmt = select(User).where(whereclause)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_credential_account(
    session: AsyncSession, user_id: str
) -> Account | None:
    stmt = select(Account).where(
        Account.user_id == user_id, Account.provider_id == "credentials"
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None

    account = await get_credential_account(db, user.id)
    if not account or not account.password:
        return None

    if not verify_password(password, account.password):
        return None

    return user


async def create_user(
    session: AsyncSession, user_create: UserPasswordSignupRequestForm
):
    user = User(
        name=user_create.name,
        email=user_create.email,
        email_verified=False,
        is_super_user=False,
    )

    session.add(user)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    account = Account(
        provider_id="credentials",
        account_id=user.id,
        user_id=user.id,
        password=hash_password(user_create.password),
    )

    session.add(account)
    await session.commit()
    await session.refresh(user)
    return user
