from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

import app.services.invites as invites_service
from app.db.db import get_database
from app.services.models.users import User
from app.api.models.groups import GroupAndUserRequest
from app.services.authentication import get_current_user

router = APIRouter()


@router.post("/group/invite", status_code=status.HTTP_201_CREATED)
async def invite_user_to_group(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return invites_service.invite_user_to_group(db, current_user, request)


@router.delete("/group/cancel")
async def cancel_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    invites_service.cancel_invite_to_group(db, current_user, invite_id)
    return "Invite cancelled"


@router.get("/group/list")
async def get_invites_to_group(group_id: int, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return invites_service.get_invites_to_group(db, current_user, group_id)


@router.post("/accept")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    invites_service.process_invite_to_group(db, current_user, invite_id, is_accept=True)
    return "Invite accepted"


@router.post("/decline")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    invites_service.process_invite_to_group(db, current_user, invite_id, is_accept=False)
    return "Invite declined"


@router.get("/list")
async def get_my_invites_to_groups(current_user: User = Depends(get_current_user),
                                   db: Session = Depends(get_database)):
    return invites_service.get_my_invites_to_groups(db, current_user)
