from typing import Annotated

from fastapi import APIRouter, Depends

from app.models import User
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/resource", tags=["resource"])


@router.post("")
async def create_resource(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
