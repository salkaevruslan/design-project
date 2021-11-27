from datetime import timedelta, datetime
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.db import get_database
from app.db.models.users import UserDB
from app.models.domain.users import User
from app.models.schemas.users import UserCreationRequest

SECRET_KEY = 'tmptoken'  # TODO
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hashed_password: str):
    return crypt_context.verify(password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_from_db(db, username)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


async def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    access_token = jwt.encode(data_to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return access_token


async def get_current_user(db: Session = Depends(get_database), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = get_user_from_db(db, username)
    if user is None:
        raise credentials_exception
    return User(id=user.id, username=user.username, email=user.email)


def get_user_from_db(db, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


def create_user(db: Session, user: UserCreationRequest):
    new_db_user = UserDB(username=user.username,
                         email=user.email,
                         password_hash=get_password_hash(user.password))
    db.add(new_db_user)
    db.commit()
    db.refresh(new_db_user)
    return new_db_user
