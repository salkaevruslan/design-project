from pydantic import BaseModel


class GroupCreationRequest(BaseModel):
    name: str


class InviteCreationRequest(BaseModel):
    group_id: int
    invited_user_name: str
