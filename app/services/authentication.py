from datetime import timedelta, datetime
from typing import Optional

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.config import get_settings
import app.db.repository.users as users_repository
from app.exceptions import user_exceptions
from app.services.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = 'HS256'
SECRET_KEY = get_settings()['secret_key']


def verify_password(password: str, hashed_password: str):
    return crypt_context.verify(password, hashed_password)


def get_password_hash(password):
    return crypt_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = users_repository.get_user_by_name_db(db, username)
    if not user or not verify_password(password, user.password_hash):
        return False
    return User(id=user.id, username=user.username, email=user.email)


async def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    access_token = jwt.encode(data_to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return access_token


def create_user(db,
                email: str,
                username: str,
                password: str):
    password_hash = get_password_hash(password)
    if users_repository.get_user_by_name_db(db, username) is not None:
        raise user_exceptions.UserAlreadyExistsException(is_name=False)
    if users_repository.get_user_by_email_db(db, username) is not None:
        raise user_exceptions.UserAlreadyExistsException(is_name=False)
    new_db_user = users_repository.create_user_db(db, email, username, password_hash)
    return User(id=new_db_user.id, username=new_db_user.username, email=new_db_user.email)
