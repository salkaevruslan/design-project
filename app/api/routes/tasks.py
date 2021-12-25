from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.services.models.users import User
from app.api.models.tasks import UserTaskCreationRequest, GroupTaskCreationRequest, GroupTaskFilterRequest, \
    TaskFilterRequest, TaskUpdateRequest
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


@router.post("/all/list")
async def all_user_tasks(request: TaskFilterRequest, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_database)):
    return tasks_service.get_all_tasks(db, current_user, request)


@router.post("/personal/list")
async def my_personal_tasks(request: TaskFilterRequest, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    return tasks_service.get_personal_tasks(db, current_user, request)


@router.post("/group/list")
async def my_group_tasks(request: GroupTaskFilterRequest, current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_database)):
    return tasks_service.get_group_tasks(db, current_user, request.group_id, request)


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


@router.delete("/group/suggestions/delete")
async def delete_suggested_task(task_id: int, current_user: User = Depends(get_current_user),
                                db: Session = Depends(get_database)):
    tasks_service.delete_suggested_task(db, current_user, task_id)
    return "Suggested task deleted"


@router.post("/group/suggestions/create", status_code=status.HTTP_201_CREATED)
async def suggest_group_task(request: GroupTaskCreationRequest, current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_database)):
    return tasks_service.create_group_task_suggestion(db, current_user, request)


@router.post("/group/suggestions/my")
async def get_my_group_task_suggestion(request: GroupTaskFilterRequest, current_user: User = Depends(get_current_user),
                                       db: Session = Depends(get_database)):
    return tasks_service.get_my_task_suggestions_to_group(db, current_user, request.group_id, request)


@router.post("/group/suggestions/all")
async def get_all_group_task_suggestion(request: GroupTaskFilterRequest, current_user: User = Depends(get_current_user),
                                        db: Session = Depends(get_database)):
    return tasks_service.get_all_task_suggestions_to_group(db, current_user, request.group_id, request)


@router.post("/group/suggestions/accept")
async def accept_task_suggestion(task_id: int, current_user: User = Depends(get_current_user),
                                 db: Session = Depends(get_database)):
    tasks_service.process_suggested_task(db, current_user, task_id, True)
    return "Task suggestion accepted"


@router.post("/group/suggestions/decline")
async def decline_task_suggestion(task_id: int, current_user: User = Depends(get_current_user),
                                  db: Session = Depends(get_database)):
    tasks_service.process_suggested_task(db, current_user, task_id, False)
    return "Task suggestion declines"


@router.post("/personal/update")
async def update_user_task(request: TaskUpdateRequest, current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_database)):
    tasks_service.update_user_task(db, current_user, request)
    return "Personal task updates"


@router.post("/group/update")
async def update_group_task(request: TaskUpdateRequest, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_database)):
    tasks_service.update_group_task(db, current_user, request)
    return "Group task updated"


@router.post("/group/suggestions/update")
async def update_suggested_task(request: TaskUpdateRequest, current_user: User = Depends(get_current_user),
                                db: Session = Depends(get_database)):
    tasks_service.update_suggested_task(db, current_user, request)
    return "Suggested task updated"
