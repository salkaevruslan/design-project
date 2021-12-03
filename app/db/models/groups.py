from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, UniqueConstraint

from app.db.db import Base
import datetime


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)


class UserInGroupDB(Base):
    __tablename__ = "group_user"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)


class InviteDB(Base):
    __tablename__ = 'invites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    datetime = Column(DateTime, default=datetime.datetime.utcnow())
    UniqueConstraint(user_id, group_id)
