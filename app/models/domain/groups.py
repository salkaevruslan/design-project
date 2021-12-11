import datetime

from pydantic import BaseModel

from app.models.domain.users import User


class Group(BaseModel):
    id: int
    name: str
    creation_datetime: datetime.datetime
    admin: User
