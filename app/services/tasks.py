from app.db.repository.tasks import create_task_db, create_user_task_db
from app.models.domain.tasks import Task
from app.models.domain.users import User
from app.models.schemas.tasks import UserTaskCreationRequest


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
