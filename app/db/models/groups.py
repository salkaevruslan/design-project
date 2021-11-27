from sqlalchemy import Integer, Column, ForeignKey, String

from app.db.db import Base


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer)
    name = Column(String)


class UserInGroupDB(Base):
    __tablename__ = "group_user"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
