import datetime

from pydantic import BaseModel

from app.services.models.users import User


class Group(BaseModel):
    id: int
    name: str
    creation_datetime: datetime.datetime
    admin: User
