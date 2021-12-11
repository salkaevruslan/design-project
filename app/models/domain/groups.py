from pydantic import BaseModel

from app.models.domain.users import User


class Group(BaseModel):
    id: int
    name: str
    admin: User
