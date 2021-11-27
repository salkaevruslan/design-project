from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest
from app.services.authentication import get_current_user
from app.services.groups import get_user_groups, create_group

router = APIRouter()


@router.get("/my-groups")
async def get_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return get_user_groups(db, current_user)


@router.post("/create")
async def create_new_group(request: GroupCreationRequest, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return create_group(db, current_user, request)
