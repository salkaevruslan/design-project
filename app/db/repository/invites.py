from app.db.models.groups import InviteDB, GroupDB
from app.db.models.users import UserDB
from app.models.enums.invite import InviteStatus


def create_invite_db(db, invited_user_id: int, group_id: int):
    new_invite_db = InviteDB(user_id=invited_user_id, group_id=group_id)
    db.add(new_invite_db)
    db.commit()
    db.refresh(new_invite_db)
    return new_invite_db


def get_invite_by_params_db(db, group_id: int, user_id: int, invite_status: InviteStatus):
    query = db.query(InviteDB)
    query = query.filter(InviteDB.user_id == user_id)
    query = query.filter(InviteDB.group_id == group_id)
    query = query.filter(InviteDB.status == invite_status)
    return query.all()


def get_invite_by_id_db(db, invite_id: int):
    return db.query(InviteDB).filter(InviteDB.id == invite_id).first()


def get_user_invites_from_db(db, user_id: int):
    query = db.query(InviteDB, GroupDB, UserDB)
    query = query.filter(InviteDB.user_id == user_id)
    query = query.join(GroupDB, InviteDB.group_id == GroupDB.id)
    query = query.join(UserDB, GroupDB.admin_id == UserDB.id)
    result = []
    for invite, group, user in query.all():
        result.append({
            'invite': invite,
            'group': group,
            'admin': user,
        })
    return result


def get_group_invites_from_db(db, group_id: int):
    query = db.query(InviteDB, UserDB)
    query = query.filter(InviteDB.group_id == group_id)
    query = query.join(UserDB, InviteDB.user_id == UserDB.id)
    result = []
    for invite, user in query.all():
        result.append({
            'invite': invite,
            'user': user,
        })
    return result
