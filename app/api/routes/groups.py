from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest
from app.services.authentication import get_current_user
import app.services.groups as groups_service
import app.services.invites as invites_service

router = APIRouter()


@router.get("/my-groups")
async def my_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_database)):
    return groups_service.get_user_groups(db, current_user)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreationRequest, current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_database)):
    return groups_service.create_group(db, current_user, request)


@router.get("/members")
async def get_group_members(group_id: int, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return groups_service.get_group_members(db, current_user, group_id)


@router.post("/invite/accept")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    invites_service.process_invite_to_group(db, current_user, invite_id, is_accept=True)
    return "Invite accepted"


@router.post("/invite/decline")
async def accept_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    invites_service.process_invite_to_group(db, current_user, invite_id, is_accept=False)
    return "Invite declined"


@router.get("/my-invites")
async def get_my_invites_to_groups(current_user: User = Depends(get_current_user),
                                   db: Session = Depends(get_database)):
    return invites_service.get_my_invites_to_groups(db, current_user)


@router.delete("/leave")
async def leave_from_group(group_id: int, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    groups_service.leave_from_group(db, current_user, group_id)
    return "Ypu leaved from group"
