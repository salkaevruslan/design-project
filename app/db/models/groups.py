from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, Enum

from app.db.db import Base
import datetime

from app.models.enums.groups import GroupRole


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    creation_datetime = Column(DateTime, default=datetime.datetime.utcnow())


class UserInGroupDB(Base):
    __tablename__ = "group_user"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    role = Column(Enum(GroupRole), default=GroupRole.MEMBER)
    member_since_datetime = Column(DateTime, default=datetime.datetime.utcnow())
