from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.tasks import UserTaskCreationRequest, GroupTaskCreationRequest
from app.services.authentication import get_current_user
import app.services.tasks as tasks_service

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user_task(request: UserTaskCreationRequest, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return tasks_service.create_user_task(db, current_user, request)


@router.post("/group/create", status_code=status.HTTP_201_CREATED)
async def create_group_task(request: GroupTaskCreationRequest, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return tasks_service.create_group_task(db, current_user, request)
