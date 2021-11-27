from pydantic import BaseModel


class GroupCreationRequest(BaseModel):
    name: str
