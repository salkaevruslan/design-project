from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, Enum

from app.db.db import Base
import datetime

from app.models.enums.invite import InviteStatus


class GroupDB(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)


class UserInGroupDB(Base):
    __tablename__ = "group_user"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    member_since_datetime = Column(DateTime, default=datetime.datetime.utcnow())


class InviteDB(Base):
    __tablename__ = 'invites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    datetime = Column(DateTime, default=datetime.datetime.utcnow())
    status = Column(Enum(InviteStatus), default=InviteStatus.SENT)
