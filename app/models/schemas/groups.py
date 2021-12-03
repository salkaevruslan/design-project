from pydantic import BaseModel
import enum


class GroupCreationRequest(BaseModel):
    name: str


class InviteStatus(enum.Enum):
    SENT = 1,
    ACCEPTED = 2,
    DECLINED = 3


class InviteCreationRequest(BaseModel):
    group_id: int
    invited_user_name: str
