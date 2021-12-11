from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.invites as invites_service
from app.db.db import get_database
from app.models.domain.users import User
from app.services.authentication import get_current_user

router = APIRouter()


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


@router.get("/my-invites")
async def get_my_invites_to_groups(current_user: User = Depends(get_current_user),
                                   db: Session = Depends(get_database)):
    return invites_service.get_my_invites_to_groups(db, current_user)
