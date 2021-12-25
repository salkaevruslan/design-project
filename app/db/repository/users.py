from sqlalchemy.orm import Session

from app.db.models.users import UserDB


def create_user_db(db: Session,
                   email: str,
                   username: str,
                   password_hash):
    new_db_user = UserDB(username=username,
                         email=email,
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
