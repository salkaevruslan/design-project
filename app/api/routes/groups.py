from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest, InviteCreationRequest
from app.services.authentication import get_current_user
from app.services.groups import get_user_groups, create_group, get_group_members, invite_user_to_group

router = APIRouter()


@router.get("/my-groups")
async def groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return get_user_groups(db, current_user)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_group(request: GroupCreationRequest, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return create_group(db, current_user, request)


@router.get("/members")
async def group_members(group_id: int, current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_database)):
    return get_group_members(db, current_user, group_id)


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_to_group(request: InviteCreationRequest, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_database)):
    return invite_user_to_group(db, current_user, request)
