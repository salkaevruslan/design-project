from sqlalchemy.orm import Session

from app.db.models.users import UserDB
from app.api.models.users import UserCreationRequest


def create_user_db(db: Session, request: UserCreationRequest, password_hash):
    new_db_user = UserDB(username=request.username,
                         email=request.email,
                         password_hash=password_hash)
    db.add(new_db_user)
    db.commit()
    db.refresh(new_db_user)
    return new_db_user


def get_user_by_name_db(db, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_user_by_email_db(db, email: str):
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_id_db(db, user_id: int):
    return db.query(UserDB).filter(UserDB.id == user_id).first()
