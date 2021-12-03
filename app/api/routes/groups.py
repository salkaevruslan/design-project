from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest, InviteCreationRequest
from app.services.authentication import get_current_user
from app.services.groups import get_user_groups, create_group, get_group_members, invite_user_to_group, \
    get_my_invites, get_list_of_invites_to_group, cancel_invite, process_invite

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


@router.delete("/invite/cancel")
async def cancel_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    cancel_invite(db, current_user, invite_id)
    return "Invite cancelled"


@router.post("/invite/accept")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    process_invite(db, current_user, invite_id, is_accept=True)
    return "Invite accepted"


@router.post("/invite/decline")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    process_invite(db, current_user, invite_id, is_accept=False)
    return "Invite declined"


@router.get("/my-invites")
async def my_invites_to_groups(current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return get_my_invites(db, current_user)


@router.get("/group-invites")
async def invites_to_group(group_id: int, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return get_list_of_invites_to_group(db, current_user, group_id)
