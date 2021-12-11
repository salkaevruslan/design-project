import datetime
from pydantic import BaseModel

from app.models.enums.tasks import TaskPriority


class TaskCreationRequest(BaseModel):
    type: str
    name: str
    description: str
    priority: TaskPriority
    start_time: datetime.datetime
