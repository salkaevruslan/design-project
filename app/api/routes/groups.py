from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest
from app.services.authentication import get_current_user
import app.services.groups as groups_service

router = APIRouter()


@router.get("/list")
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


@router.delete("/leave")
async def leave_from_group(group_id: int, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    groups_service.leave_from_group(db, current_user, group_id)
    return "You leaved from group"
