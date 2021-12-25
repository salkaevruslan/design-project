import datetime

from fastapi import HTTPException, status

import app.db.repository.groups as groups_repository
import app.db.repository.tasks as tasks_repository
from app.services.models.tasks import Task
from app.services.models.users import User
from app.models.enums.tasks import TaskOwnerType, TaskStatus, TaskPriority, TaskType
from app.services.groups import get_group_as_member
from app.services.groups_admin import get_group_as_admin


def get_task(db, task_id: int):
    task = tasks_repository.get_task_by_id_db(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task not found"
        )
    return task


def get_task_owner_type(db, task_id: int):
    if tasks_repository.get_user_task_db(db, task_id):
        return TaskOwnerType.PERSONAL
    if tasks_repository.get_group_task_db(db, task_id):
        return TaskOwnerType.GROUP
    if tasks_repository.get_group_task_suggestion_db(db, task_id):
        return TaskOwnerType.GROUP_SUGGESTED
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Task owner type not found"
    )


def create_user_task(db, current_user: User,
                     task_type: TaskType,
                     task_name: str,
                     description: str,
                     priority: TaskPriority,
                     start_time: datetime.datetime):
    new_db_task = tasks_repository.create_task_db(db, task_type, task_name, description, priority, start_time)
    tasks_repository.create_user_task_db(db, current_user.id, new_db_task.id)
    return Task(
        id=new_db_task.id,
        type=new_db_task.type,
        status=new_db_task.status,
        creation_datetime=new_db_task.creation_datetime,
        name=new_db_task.name,
        description=new_db_task.description,
        priority=new_db_task.priority,
        start_time=new_db_task.start_time
    )


def create_group_task_suggestion(db, current_user: User,
                                 group_id: int,
                                 task_type: TaskType,
                                 task_name: str,
                                 description: str,
                                 priority: TaskPriority,
                                 start_time: datetime.datetime):
    get_group_as_member(db, current_user, group_id)
    new_db_task = tasks_repository.create_task_db(db, task_type, task_name,
                                                  description, priority, start_time, TaskStatus.SUGGESTED)
    tasks_repository.create_group_task_suggestion_db(db, current_user.id, group_id, new_db_task.id)
    return Task(
        id=new_db_task.id,
        type=new_db_task.type,
        status=new_db_task.status,
        creation_datetime=new_db_task.creation_datetime,
        name=new_db_task.name,
        description=new_db_task.description,
        priority=new_db_task.priority,
        start_time=new_db_task.start_time
    )


def create_group_task(db, current_user: User,
                      group_id: int,
                      task_type: TaskType,
                      task_name: str,
                      description: str,
                      priority: TaskPriority,
                      start_time: datetime.datetime):
    get_group_as_admin(db, current_user, group_id)
    new_db_task = tasks_repository.create_task_db(db, task_type, task_name, description, priority, start_time)
    tasks_repository.create_group_task_db(db, group_id, new_db_task.id)
    return Task(
        id=new_db_task.id,
        type=new_db_task.type,
        creation_datetime=new_db_task.creation_datetime,
        name=new_db_task.name,
        description=new_db_task.description,
        priority=new_db_task.priority,
        start_time=new_db_task.start_time
    )


def get_personal_tasks(db, current_user: User,
                       period_start: datetime.datetime,
                       period_end: datetime.datetime,
                       task_type: TaskType,
                       priority: TaskPriority):
    result = tasks_repository.get_personal_tasks_db(db, current_user.id, period_start, period_end, task_type, priority)
    response = []
    for task in result:
        response.append(
            Task(
                id=task.id,
                type=task.type,
                status=task.status,
                creation_datetime=task.creation_datetime,
                name=task.name,
                description=task.description,
                priority=task.priority,
                start_time=task.start_time
            )
        )
    return response


def get_group_tasks(db, current_user: User,
                    group_id: int,
                    period_start: datetime.datetime,
                    period_end: datetime.datetime,
                    task_type: TaskType,
                    priority: TaskPriority):
    get_group_as_member(db, current_user, group_id)
    result = tasks_repository.get_group_tasks_db(db, group_id, period_start, period_end, task_type, priority)
    response = []
    for task in result:
        response.append(
            Task(
                id=task.id,
                type=task.type,
                status=task.status,
                creation_datetime=task.creation_datetime,
                name=task.name,
                description=task.description,
                priority=task.priority,
                start_time=task.start_time
            )
        )
    return response


def get_all_tasks(db, current_user: User,
                  period_start: datetime.datetime,
                  period_end: datetime.datetime,
                  task_type: TaskType,
                  priority: TaskPriority):
    response = []
    personal_tasks = get_personal_tasks(db, current_user, period_start, period_end, task_type, priority)
    for task in personal_tasks:
        response.append({
            'owner': TaskOwnerType.PERSONAL,
            'owner_id': current_user.id,
            'task': task
        })
    groups_info = groups_repository.get_user_groups_from_db(db, current_user.id)
    for info in groups_info:
        group_tasks = get_group_tasks(db, current_user, info['group'].id, period_start, period_end, task_type, priority)
        for task in group_tasks:
            response.append({
                'owner': TaskOwnerType.GROUP,
                'owner_id': info['group'].id,
                'task': task
            })
    return response


def delete_user_task(db, current_user: User, task_id: int):
    task = get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.PERSONAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not personal"
        )
    user_task_db = tasks_repository.get_user_task_db(db, task_id)
    if not user_task_db or user_task_db.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not assigned to you"
        )
    tasks_repository.delete_user_task_db(db, task_id)
    db.delete(task)
    db.commit()


def delete_group_task(db, current_user: User, task_id: int):
    task = get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.GROUP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not a group task"
        )
    group_task_db = tasks_repository.get_group_task_db(db, task_id)
    get_group_as_admin(db, current_user, group_task_db.group_id)
    tasks_repository.delete_group_task_db(db, task_id)
    db.delete(task)
    db.commit()


def delete_suggested_task(db, current_user: User, task_id: int):
    task = get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.GROUP_SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not a suggested task"
        )
    suggested_task_db = tasks_repository.get_group_task_suggestion_db(db, task_id)
    if suggested_task_db.user_id != current_user.id:
        get_group_as_admin(db, current_user, suggested_task_db.group_id)
    else:
        get_group_as_member(db, current_user, suggested_task_db.group_id)
    tasks_repository.delete_group_task_db(db, task_id)
    db.delete(task)
    db.commit()


def get_my_task_suggestions_to_group(db, current_user: User,
                                     group_id: int,
                                     period_start: datetime.datetime,
                                     period_end: datetime.datetime,
                                     task_type: TaskType,
                                     priority: TaskPriority):
    get_group_as_member(db, current_user, group_id)
    result = tasks_repository.get_user_suggestions_to_group_db(db, current_user.id, group_id, period_start, period_end,
                                                               task_type, priority)
    response = []
    for task in result:
        response.append(
            Task(
                id=task.id,
                type=task.type,
                status=task.status,
                creation_datetime=task.creation_datetime,
                name=task.name,
                description=task.description,
                priority=task.priority,
                start_time=task.start_time
            )
        )
    return response


def get_all_task_suggestions_to_group(db, current_user: User,
                                      group_id: int,
                                      period_start: datetime.datetime,
                                      period_end: datetime.datetime,
                                      task_type: TaskType,
                                      priority: TaskPriority):
    get_group_as_admin(db, current_user, group_id)
    result = tasks_repository.get_suggestions_to_group_db(db, group_id, period_start, period_end, task_type, priority)
    response = []
    for elem in result:
        task = elem['task']
        response.append(
            {
                'user_id': elem['user_id'],
                'task': Task(
                    id=task.id,
                    type=task.type,
                    status=task.status,
                    creation_datetime=task.creation_datetime,
                    name=task.name,
                    description=task.description,
                    priority=task.priority,
                    start_time=task.start_time
                )
            })
    return response


def process_suggested_task(db, current_user: User, task_id: int, is_accept: bool):
    task = get_task(db, task_id)
    group_task_suggestion_db = tasks_repository.get_group_task_suggestion_db(db, task_id)
    if not group_task_suggestion_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task suggestion not found"
        )
    get_group_as_admin(db, current_user, group_task_suggestion_db.group_id)
    if is_accept:
        task.status = TaskStatus.ACTIVE
        tasks_repository.create_group_task_db(db, group_task_suggestion_db.group_id, task_id)
        db.delete(group_task_suggestion_db)
        db.commit()
        db.refresh(task)
    else:
        db.delete(group_task_suggestion_db)
        db.delete(task)
        db.commit()


def update_user_task(db, current_user: User,
                     task_id: int,
                     task_status: TaskStatus,
                     task_type: TaskType,
                     description: str,
                     priority: TaskPriority,
                     start_time: datetime.datetime):
    get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.PERSONAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not personal"
        )
    user_task_db = tasks_repository.get_user_task_db(db, task_id)
    if not user_task_db or user_task_db.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not assigned to you"
        )
    if status == TaskStatus.SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't change task status to {TaskStatus.SUGGESTED}"
        )
    tasks_repository.apply_task_update_db(db, task_id, task_status, task_type, description, priority, start_time)


def update_group_task(db, current_user: User,
                      task_id: int,
                      task_status: TaskStatus,
                      task_type: TaskType,
                      description: str,
                      priority: TaskPriority,
                      start_time: datetime.datetime):
    get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.GROUP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not a group task"
        )
    group_task_db = tasks_repository.get_group_task_db(db, task_id)
    if group_task_db.user_id == current_user.id:
        get_group_as_member(db, current_user, group_task_db.group_id)
    else:
        get_group_as_admin(db, current_user, group_task_db.group_id)
    if status == TaskStatus.SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't change task status to {TaskStatus.SUGGESTED}"
        )
    tasks_repository.apply_task_update_db(db, task_id, task_status, task_type, description, priority, start_time)


def update_suggested_task(db, current_user: User,
                          task_id: int,
                          task_status: TaskStatus,
                          task_type: TaskType,
                          description: str,
                          priority: TaskPriority,
                          start_time: datetime.datetime):
    get_task(db, task_id)
    if get_task_owner_type(db, task_id) != TaskOwnerType.GROUP_SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This task is not a suggested task"
        )
    group_task_db = tasks_repository.get_group_task_suggestion_db(db, task_id)
    if group_task_db.user_id == current_user.id:
        get_group_as_member(db, current_user, group_task_db.group_id)
    else:
        get_group_as_admin(db, current_user, group_task_db.group_id)
    if status != TaskStatus.SUGGESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can change task status for suggested task"
        )
    tasks_repository.apply_task_update_db(db, task_id, task_status, task_type, description, priority, start_time)
