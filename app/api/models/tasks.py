import datetime
from pydantic import BaseModel

from app.models.enums.tasks import TaskPriority, TaskType, TaskStatus


class UserTaskCreationRequest(BaseModel):
    type: TaskType = TaskType.UNDEFINED
    name: str
    description: str = None
    priority: TaskPriority = TaskPriority.MEDIUM
    start_time: datetime.datetime = None


class GroupTaskCreationRequest(UserTaskCreationRequest):
    group_id: int


class TaskFilterRequest(BaseModel):
    period_start: datetime.datetime = None
    period_end: datetime.datetime = None
    type: TaskType = None
    priority: TaskPriority = None


class GroupTaskFilterRequest(TaskFilterRequest):
    group_id: int


class TaskUpdateRequest(BaseModel):
    task_id: int
    status: TaskStatus = None
    type: TaskType = None
    description: str = None
    priority: TaskPriority = None
    start_time: datetime.datetime = None
