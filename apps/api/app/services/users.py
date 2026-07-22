from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument

from app.core.security import hash_password, verify_password
from app.models import (
    Account,
    GoogleOAuthResponse,
    User,
)


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


async def create_user_password(
    session: AsyncSession, user: User, password: str
):
    session.add(user)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise

    account = Account(
        provider_id="credentials",
        account_id=user.id,
        user_id=user.id,
        password=hash_password(password),
    )

    session.add(account)
    await session.commit()
    await session.refresh(user)
    return user


async def get_account_by_provider(
    session: AsyncSession, provider_id: str, account_id: str
) -> Account | None:
    stmt = select(Account).where(
        Account.provider_id == provider_id, Account.account_id == account_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_provider(
    session: AsyncSession, token: GoogleOAuthResponse
) -> User:
    userinfo = token.userinfo

    account = await get_account_by_provider(session, "google", userinfo.sub)
    if account:
        account.access_token = token.access_token
        account.id_token = token.id_token
        account.access_token_expires_at = datetime.fromtimestamp(
            token.expires_at
        )
        account.scope = token.scope
        await session.commit()
        # TODO: I don't think its good to use typing.cast here
        return cast(User, await get_user(session, User.id == account.user_id))

    user = User(
        name=userinfo.name,
        email=userinfo.email,
        email_verified=userinfo.email_verified,
        image=userinfo.picture,
        is_super_user=False,
    )
    session.add(user)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise

    account = Account(
        account_id=userinfo.sub,
        provider_id="google",
        user_id=user.id,
        access_token=token.access_token,
        id_token=token.id_token,
        access_token_expires_at=datetime.fromtimestamp(token.expires_at),
        scope=token.scope,
    )

    session.add(account)
    await session.commit()
    await session.refresh(user)
    return user
