from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_active_user
from app.models import User
from app.models.organization import OrganizationCreate
from app.services.organizations import create_organization

router = APIRouter(prefix="/organization", tags=["organization"])


@router.post("", summary="Create an Organization")
async def post_organization(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    payload: OrganizationCreate,
):
    try:
        organization = await create_organization(session, payload, current_user)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while trying to create an organization",
        )
    return organization
