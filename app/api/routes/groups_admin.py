from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import InviteCreationRequest, AdminChangeRequest
from app.services.authentication import get_current_user
import app.services.groups_admin as admin_service

router = APIRouter()


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_user_to_group(request: InviteCreationRequest, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return admin_service.invite_user_to_group(db, current_user, request)


@router.delete("/invite/cancel")
async def cancel_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    admin_service.cancel_invite_to_group(db, current_user, invite_id)
    return "Invite cancelled"


@router.get("/group-invites")
async def get_invites_to_group(group_id: int, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return admin_service.get_invites_to_group(db, current_user, group_id)


@router.post("/change-admin")
async def change_group_admin(request: AdminChangeRequest, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    admin_service.change_group_admin(db, current_user, request)
    return f"{request.user_name} is now admin of this group"
