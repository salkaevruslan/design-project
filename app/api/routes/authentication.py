from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.models.domain.users import User
from app.models.schemas.authentication import TokenResponse
from app.services.authentication import generate_access_token, authenticate_user

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(db: Session = Depends(get_database), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_obj = User(id=user.id, username=user.username, email=user.email)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await generate_access_token(
        data={"sub": user_obj.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
