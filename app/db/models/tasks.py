import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum

from app.db.db import Base
from app.models.enums.tasks import TaskPriority


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    creation_datetime = Column(DateTime, default=datetime.datetime.utcnow)
    name = Column(String)
    description = Column(String)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    start_time = Column(DateTime, nullable=True)
