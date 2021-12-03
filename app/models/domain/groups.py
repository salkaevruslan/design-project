from pydantic import BaseModel
import datetime


class Group(BaseModel):
    id: int
    name: str
    admin_id: int


class Invite(BaseModel):
    id: int
    group_id: int
    invited_user_id: int
    datetime: datetime.datetime
