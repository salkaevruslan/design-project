from app.db.models.tasks import TaskDB, UserTaskDB, GroupTaskDB
from app.models.schemas.tasks import UserTaskCreationRequest


def create_task_db(db, request: UserTaskCreationRequest):
    new_db_task = TaskDB(type=request.type,
                         name=request.name,
                         description=request.description,
                         priority=request.priority,
                         start_time=request.start_time)
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


def get_task_by_id_db(db, task_id: int):
    return db.query(TaskDB).filter(TaskDB.id == task_id).first()


def find_user_task_db(db, task_id: int):
    query = db.query(UserTaskDB)
    query = query.filter(UserTaskDB.task_id == task_id)
    return query.first()


def find_group_task_db(db, task_id: int):
    query = db.query(GroupTaskDB)
    query = query.filter(GroupTaskDB.task_id == task_id)
    return query.first()


def delete_user_task_db(db, task_id: int):
    user_task_db = find_user_task_db(db, task_id)
    if user_task_db:
        db.delete(user_task_db)
        db.commit()


def delete_group_task_db(db, task_id: int):
    group_task_db = find_group_task_db(db, task_id)
    if group_task_db:
        db.delete(group_task_db)
        db.commit()


def get_personal_tasks_db(db, user_id: int):
    query = db.query(UserTaskDB, TaskDB)
    query = query.filter(UserTaskDB.user_id == user_id)
    query = query.join(TaskDB, UserTaskDB.task_id == TaskDB.id)
    result = []
    for user_task, task in query.all():
        result.append(task)
    return result


def get_group_tasks_db(db, group_id: int):
    query = db.query(GroupTaskDB, TaskDB)
    query = query.filter(GroupTaskDB.group_id == group_id)
    query = query.join(TaskDB, GroupTaskDB.task_id == TaskDB.id)
    result = []
    for group_task, task in query.all():
        result.append(task)
    return result
