from fastapi import HTTPException, status

from app.db.repository.tasks import create_task_db, create_user_task_db, create_group_task_db, get_task_by_id_db, \
    find_user_task_db, delete_user_task_db, get_personal_tasks_db, get_group_tasks_db, find_group_task_db, \
    delete_group_task_db
from app.models.domain.tasks import Task
from app.models.domain.users import User
from app.models.schemas.tasks import UserTaskCreationRequest, GroupTaskCreationRequest
from app.services.groups import get_group_as_member
from app.services.groups_admin import get_group_as_admin


def get_task(db, task_id: int):
    task = get_task_by_id_db(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task not found"
        )
    return task


def create_user_task(db, current_user: User, request: UserTaskCreationRequest):
    new_db_task = create_task_db(db, request)
    create_user_task_db(db, current_user.id, new_db_task.id)
    return Task(
        id=new_db_task.id,
        type=new_db_task.type,
        creation_datetime=new_db_task.creation_datetime,
        name=new_db_task.name,
        description=new_db_task.name,
        priority=new_db_task.priority,
        start_time=new_db_task.start_time
    )


def create_group_task(db, current_user: User, request: GroupTaskCreationRequest):
    get_group_as_admin(db, current_user, request.group_id)
    new_db_task = create_task_db(db, request)
    create_group_task_db(db, request.group_id, new_db_task.id)
    return Task(
        id=new_db_task.id,
        type=new_db_task.type,
        creation_datetime=new_db_task.creation_datetime,
        name=new_db_task.name,
        description=new_db_task.name,
        priority=new_db_task.priority,
        start_time=new_db_task.start_time
    )


def get_personal_tasks(db, current_user: User):
    result = get_personal_tasks_db(db, current_user.id)
    response = []
    for task in result:
        response.append(
            Task(
                id=task.id,
                type=task.type,
                creation_datetime=task.creation_datetime,
                name=task.name,
                description=task.name,
                priority=task.priority,
                start_time=task.start_time
            )
        )
    return response


def get_group_tasks(db, current_user: User, group_id: int):
    get_group_as_member(db, current_user, group_id)
    result = get_group_tasks_db(db, group_id)
    response = []
    for task in result:
        response.append(
            Task(
                id=task.id,
                type=task.type,
                creation_datetime=task.creation_datetime,
                name=task.name,
                description=task.name,
                priority=task.priority,
                start_time=task.start_time
            )
        )
    return response


def delete_user_task(db, current_user: User, task_id: int):
    task = get_task(db, task_id)
    user_task_db = find_user_task_db(db, task_id)
    if not user_task_db or user_task_db.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not assigned to you"
        )
    delete_user_task_db(db, task_id)
    db.delete(task)
    db.commit()


def delete_group_task(db, current_user: User, task_id: int):
    task = get_task(db, task_id)
    group_task_db = find_group_task_db(db, task_id)
    get_group_as_admin(db, current_user, group_task_db.group_id)
    delete_group_task_db(db, task_id)
    db.delete(task)
    db.commit()
