from pydantic import BaseModel

from app.models.enums.invite import InviteStatus
import datetime


class Invite(BaseModel):
    id: int
    group_id: int
    invited_user_id: int
    status: InviteStatus
    datetime: datetime.datetime
