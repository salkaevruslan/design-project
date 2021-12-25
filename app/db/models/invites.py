import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum

from app.db.db import Base
from app.models.enums.invite import InviteStatus


class InviteDB(Base):
    __tablename__ = 'invites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    datetime = Column(DateTime, default=datetime.datetime.utcnow())
    status = Column(Enum(InviteStatus), default=InviteStatus.SENT)
