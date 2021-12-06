from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import InviteCreationRequest
from app.services.authentication import get_current_user
from app.services.groups_admin import invite_user_to_group, cancel_invite, get_list_of_invites_to_group

router = APIRouter()


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_to_group(request: InviteCreationRequest, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_database)):
    return invite_user_to_group(db, current_user, request)


@router.delete("/invite/cancel")
async def cancel_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    cancel_invite(db, current_user, invite_id)
    return "Invite cancelled"


@router.get("/group-invites")
async def invites_to_group(group_id: int, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return get_list_of_invites_to_group(db, current_user, group_id)
