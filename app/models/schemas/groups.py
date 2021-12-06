from pydantic import BaseModel
import enum


class GroupCreationRequest(BaseModel):
    name: str


class InviteStatus(enum.Enum):
    SENT = "SENT",
    ACCEPTED = "ACCEPTED",
    DECLINED = "DECLINED"


class InviteCreationRequest(BaseModel):
    group_id: int
    invited_user_name: str


class AdminChangeRequest(BaseModel):
    group_id: int
    user_name: str
