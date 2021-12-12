from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.tasks import UserTaskCreationRequest, GroupTaskCreationRequest
from app.services.authentication import get_current_user
import app.services.tasks as tasks_service

router = APIRouter()


@router.post("/personal/create", status_code=status.HTTP_201_CREATED)
async def create_user_task(request: UserTaskCreationRequest, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    return tasks_service.create_user_task(db, current_user, request)


@router.post("/group/create", status_code=status.HTTP_201_CREATED)
async def create_group_task(request: GroupTaskCreationRequest, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return tasks_service.create_group_task(db, current_user, request)


@router.get("/all/list")
async def all_user_tasks(current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_database)):
    return tasks_service.get_all_tasks(db, current_user)


@router.get("/personal/list")
async def my_personal_tasks(current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return tasks_service.get_personal_tasks(db, current_user)


@router.get("/group/list")
async def my_group_tasks(group_id: int, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_database)):
    return tasks_service.get_group_tasks(db, current_user, group_id)


@router.delete("/personal/delete")
async def delete_user_task(task_id: int, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    tasks_service.delete_user_task(db, current_user, task_id)
    return "Personal task deleted"


@router.delete("/group/delete")
async def delete_group_task(task_id: int, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    tasks_service.delete_group_task(db, current_user, task_id)
    return "Group task deleted"


@router.post("/group/suggestions/create", status_code=status.HTTP_201_CREATED)
async def suggest_group_task(request: GroupTaskCreationRequest, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    return tasks_service.create_group_task_suggestion(db, current_user, request)


@router.get("/group/suggestions/my", status_code=status.HTTP_201_CREATED)
async def suggest_group_task(group_id: int, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    return tasks_service.get_my_task_suggestions_to_group(db, current_user, group_id)
