from pydantic import BaseModel
import enum


class GroupCreationRequest(BaseModel):
    name: str


class InviteStatus(enum.Enum):
    SENT = "SENT",
    ACCEPTED = "ACCEPTED",
    DECLINED = "DECLINED"


class GroupAndUserRequest(BaseModel):
    group_id: int
    user_name: str
