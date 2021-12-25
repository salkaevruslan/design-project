from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.authentication import get_current_user
from app.db.db import get_database
from app.services.models.users import User
from app.api.models.groups import GroupAndUserRequest
import app.services.groups_admin as admin_service

router = APIRouter()


@router.post("/change-admin")
async def change_group_admin(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    admin_service.change_group_admin(db, current_user, request.group_id, request.user_name)
    return f"{request.user_name} is now admin of this group"


@router.delete("/kick")
async def kick_user_from_group(request: GroupAndUserRequest, current_user: User = Depends(get_current_user),
                               db: Session = Depends(get_database)):
    admin_service.kick_user_from_group(db, current_user, request.group_id, request.user_name)
    return f"{request.user_name} is kicked from group"


@router.delete("/delete")
async def delete_group(group_id: int, current_user: User = Depends(get_current_user),
                       db: Session = Depends(get_database)):
    admin_service.delete_group(db, current_user, group_id)
    return f"Group successfully deleted"
