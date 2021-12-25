from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.routes.authentication import get_current_user
from app.db.db import get_database
from app.services.models.users import User
from app.api.models.users import UserCreationRequest
import app.services.authentication as auth_service

router = APIRouter()


@router.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreationRequest, db: Session = Depends(get_database)):
    return auth_service.create_user(db, request.email, request.username, request.password)
