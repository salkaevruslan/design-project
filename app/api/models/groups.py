from pydantic import BaseModel


class GroupCreationRequest(BaseModel):
    name: str


class GroupAndUserRequest(BaseModel):
    group_id: int
    user_name: str
