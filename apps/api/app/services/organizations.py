from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, User
from app.models.organization import OrganizationCreate


async def create_organization(
    session: AsyncSession, input: OrganizationCreate, user: User
):
    organization = Organization(name=input.name, owner_id=user.id)

    session.add(organization)
    await session.commit()
    await session.refresh(organization)
    return organization
