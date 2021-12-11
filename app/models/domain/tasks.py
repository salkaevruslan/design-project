import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.enums.tasks import TaskPriority


class Task(BaseModel):
    id: int
    type: str
    creation_datetime: datetime.datetime
    name: str
    description: str
    priority: TaskPriority
    start_time: Optional[datetime.datetime]
