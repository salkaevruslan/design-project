import datetime
from pydantic import BaseModel

from app.models.enums.tasks import TaskPriority


class UserTaskCreationRequest(BaseModel):
    type: str
    name: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    start_time: datetime.datetime = None


class GroupTaskCreationRequest(UserTaskCreationRequest):
    group_id: int
