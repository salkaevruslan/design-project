from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.users import UserCreationRequest
from app.services.authentication import get_current_user, create_user

router = APIRouter()


@router.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/add")
def add_user(user: UserCreationRequest, db: Session = Depends(get_database)):
    return create_user(db=db, user=user)