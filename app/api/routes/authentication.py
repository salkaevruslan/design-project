from datetime import timedelta

import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.api.models.authentication import TokenResponse
import app.services.authentication as auth_service
from app.services.models.users import User
import app.db.repository.users as users_repository

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(db: Session = Depends(get_database), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await auth_service.generate_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(db: Session = Depends(get_database), token: str = Depends(auth_service.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = users_repository.get_user_by_name_db(db, username)
    if user is None:
        raise credentials_exception
    return User(id=user.id, username=user.username, email=user.email)
