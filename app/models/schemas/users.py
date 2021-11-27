from pydantic import BaseModel


class UserCreationRequest(BaseModel):
    email: str
    username: str
    password: str
