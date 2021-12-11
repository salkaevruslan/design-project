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
