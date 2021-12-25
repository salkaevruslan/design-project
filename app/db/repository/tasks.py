import datetime

from app.db.models.tasks import TaskDB, UserTaskDB, GroupTaskDB, GroupTaskSuggestionDB
from app.models.enums.tasks import TaskStatus, TaskType, TaskPriority


def create_task_db(db,
                   task_type: TaskType,
                   name: str,
                   description: str,
                   priority: TaskPriority,
                   start_time: datetime.datetime,
                   status: TaskStatus = TaskStatus.ACTIVE):
    new_db_task = TaskDB(type=task_type,
                         status=status,
                         name=name,
                         description=description,
                         priority=priority,
                         start_time=start_time)
    db.add(new_db_task)
    db.commit()
    db.refresh(new_db_task)
    return new_db_task


def create_user_task_db(db, user_id: int, task_id: int):
    user_task = UserTaskDB(user_id=user_id, task_id=task_id)
    db.add(user_task)
    db.commit()
    db.refresh(user_task)
    return user_task


def create_group_task_db(db, group_id: int, task_id: int):
    group_task = GroupTaskDB(group_id=group_id, task_id=task_id)
    db.add(group_task)
    db.commit()
    db.refresh(group_task)
    return group_task


def create_group_task_suggestion_db(db, user_id, group_id: int, task_id: int):
    group_task_suggestion = GroupTaskSuggestionDB(group_id=group_id, user_id=user_id, task_id=task_id)
    db.add(group_task_suggestion)
    db.commit()
    db.refresh(group_task_suggestion)
    return group_task_suggestion


def get_task_by_id_db(db, task_id: int):
    return db.query(TaskDB).filter(TaskDB.id == task_id).first()


def get_user_task_db(db, task_id: int):
    query = db.query(UserTaskDB)
    query = query.filter(UserTaskDB.task_id == task_id)
    return query.first()


def get_group_task_db(db, task_id: int):
    query = db.query(GroupTaskDB)
    query = query.filter(GroupTaskDB.task_id == task_id)
    return query.first()


def get_group_task_suggestion_db(db, task_id: int):
    query = db.query(GroupTaskSuggestionDB)
    query = query.filter(GroupTaskSuggestionDB.task_id == task_id)
    return query.first()


def delete_user_task_db(db, task_id: int):
    user_task_db = get_user_task_db(db, task_id)
    if user_task_db:
        db.delete(user_task_db)
        db.commit()


def delete_group_task_db(db, task_id: int):
    group_task_db = get_group_task_db(db, task_id)
    if group_task_db:
        db.delete(group_task_db)
        db.commit()


def get_personal_tasks_db(db, user_id: int,
                          period_start: datetime.datetime,
                          period_end: datetime.datetime,
                          task_type: TaskType,
                          priority: TaskPriority):
    query = db.query(UserTaskDB, TaskDB)
    query = query.filter(UserTaskDB.user_id == user_id)
    query = query.join(TaskDB, UserTaskDB.task_id == TaskDB.id)
    query = apply_tasks_filters(query, period_start, period_end, task_type, priority)
    result = []
    for user_task, task in query.all():
        result.append(task)
    return result


def get_group_tasks_db(db, group_id: int,
                       period_start: datetime.datetime,
                       period_end: datetime.datetime,
                       task_type: TaskType,
                       priority: TaskPriority):
    query = db.query(GroupTaskDB, TaskDB)
    query = query.filter(GroupTaskDB.group_id == group_id)
    query = query.join(TaskDB, GroupTaskDB.task_id == TaskDB.id)
    query = apply_tasks_filters(query, period_start, period_end, task_type, priority)
    result = []
    for group_task, task in query.all():
        result.append(task)
    return result


def get_user_suggestions_to_group_db(db, user_id: int, group_id: int,
                                     period_start: datetime.datetime,
                                     period_end: datetime.datetime,
                                     task_type: TaskType,
                                     priority: TaskPriority):
    query = db.query(GroupTaskSuggestionDB, TaskDB)
    query = query.filter(GroupTaskSuggestionDB.group_id == group_id)
    query = query.filter(GroupTaskSuggestionDB.user_id == user_id)
    query = query.join(TaskDB, GroupTaskSuggestionDB.task_id == TaskDB.id)
    query = apply_tasks_filters(query, period_start, period_end, task_type, priority)
    result = []
    for group_task_suggestion, task in query.all():
        result.append(task)
    return result


def get_suggestions_to_group_db(db, group_id: int,
                                period_start: datetime.datetime,
                                period_end: datetime.datetime,
                                task_type: TaskType,
                                priority: TaskPriority):
    query = db.query(GroupTaskSuggestionDB, TaskDB)
    query = query.filter(GroupTaskSuggestionDB.group_id == group_id)
    query = query.join(TaskDB, GroupTaskSuggestionDB.task_id == TaskDB.id)
    query = apply_tasks_filters(query, period_start, period_end, task_type, priority)
    result = []
    for group_task_suggestion, task in query.all():
        result.append({
            'user_id': group_task_suggestion.user_id,
            'task': task
        })
    return result


def apply_tasks_filters(query,
                        period_start: datetime.datetime,
                        period_end: datetime.datetime,
                        task_type: TaskType,
                        priority: TaskPriority):
    if task_type is not None:
        query = query.filter(TaskDB.type == task_type)
    if priority is not None:
        query = query.filter(TaskDB.priority == priority)
    if period_start is not None:
        query = query.filter(TaskDB.start_time >= period_start)
    if period_end is not None:
        query = query.filter(TaskDB.start_time <= period_end)
    return query


def apply_task_update_db(db,
                         task_id: int,
                         status: TaskStatus,
                         task_type: TaskType,
                         description: str,
                         priority: TaskPriority,
                         start_time: datetime.datetime):
    task = get_task_by_id_db(db, task_id)
    if status is not None:
        task.status = status
    if task_type is not None:
        task.type = task_type
    if priority is not None:
        task.priority = priority
    if description is not None:
        task.description = description
    if start_time is not None:
        task.start_time = start_time
    db.commit()
    db.refresh(task)
