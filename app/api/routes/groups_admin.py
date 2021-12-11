from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupAndUserRequest
from app.models.schemas.tasks import GroupTaskCreationRequest
from app.services.authentication import get_current_user
import app.services.groups_admin as admin_service

router = APIRouter()


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_user_to_group(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return admin_service.invite_user_to_group(db, current_user, request)


@router.delete("/invites/cancel")
async def cancel_invite_to_group(invite_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    admin_service.cancel_invite_to_group(db, current_user, invite_id)
    return "Invite cancelled"


@router.get("/group-invites")
async def get_invites_to_group(group_id: int, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    return admin_service.get_invites_to_group(db, current_user, group_id)


@router.post("/change-admin")
async def change_group_admin(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    admin_service.change_group_admin(db, current_user, request)
    return f"{request.user_name} is now admin of this group"


@router.delete("/kick")
async def kick_user_from_group(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    admin_service.kick_user_from_group(db, current_user, request)
    return f"{request.user_name} is kicked from group"


@router.delete("/delete")
async def delete_group(group_id: int, current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_database)):
    admin_service.delete_group(db, current_user, group_id)
    return f"Group successfully deleted"


@router.post("/tasks/create", status_code=status.HTTP_201_CREATED)
async def create_group_task(request: GroupTaskCreationRequest, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return admin_service.create_group_task(db, current_user, request)
