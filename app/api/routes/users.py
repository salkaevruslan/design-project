from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.users import UserCreationRequest
from app.services.authentication import get_current_user
import app.services.authentication as auth_service

router = APIRouter()


@router.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreationRequest, db: Session = Depends(get_database)):
    return auth_service.create_user(db, request)
