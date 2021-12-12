import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums.tasks import TaskPriority, TaskStatus, TaskType


class Task(BaseModel):
    id: int
    type: TaskType
    status: TaskStatus
    creation_datetime: datetime.datetime
    name: str
    description: str
    priority: TaskPriority
    start_time: Optional[datetime.datetime]
