from pydantic import BaseModel
import datetime

from app.models.domain.users import User


class Group(BaseModel):
    id: int
    name: str
    admin: User


class Invite(BaseModel):
    id: int
    group_id: int
    invited_user_id: int
    datetime: datetime.datetime
