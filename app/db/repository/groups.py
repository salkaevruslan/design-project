from app.db.models.groups import GroupDB, UserInGroupDB
from app.db.models.users import UserDB
from app.models.enums.groups import GroupRole


def create_group_db(db, group_name: str):
    new_db_group = GroupDB(name=group_name)
    db.add(new_db_group)
    db.commit()
    db.refresh(new_db_group)
    return new_db_group


def get_group_by_id_db(db, group_id: int):
    return db.query(GroupDB).filter(GroupDB.id == group_id).first()


def create_user_in_group_db(db, user_id: int, group_id: int, role: GroupRole = GroupRole.MEMBER):
    user_in_group_db = UserInGroupDB(user_id=user_id, group_id=group_id, role=role)
    db.add(user_in_group_db)
    db.commit()
    db.refresh(user_in_group_db)
    return user_in_group_db


def find_user_in_group_db(db, user_id: int, group_id: int):
    query = db.query(UserInGroupDB)
    query = query.filter(UserInGroupDB.user_id == user_id)
    query = query.filter(UserInGroupDB.group_id == group_id)
    return query.first()


def find_admin_in_group_db(db, group_id: int):
    query = db.query(UserInGroupDB)
    query = query.filter(UserInGroupDB.role == GroupRole.ADMIN)
    query = query.filter(UserInGroupDB.group_id == group_id)
    return query.first()


def delete_user_in_group_db(db, user_id: int, group_id: int):
    user_in_group_db = find_user_in_group_db(db, user_id, group_id)
    if user_in_group_db:
        db.delete(user_in_group_db)
        db.commit()


def get_user_groups_from_db(db, username: str):
    query = db.query(UserDB, UserInGroupDB, GroupDB)
    query = query.filter(UserDB.username == username)
    query = query.join(UserInGroupDB, UserInGroupDB.user_id == UserDB.id)
    query = query.join(GroupDB, UserInGroupDB.group_id == GroupDB.id)
    result = []
    for user, user_in_group, group in query.all():
        result.append({
            'role': user_in_group.role,
            'group': group
        })
    return result


def get_users_in_group_from_db(db, group_id: int):
    query = db.query(GroupDB, UserInGroupDB, UserDB)
    query = query.filter(GroupDB.id == group_id)
    query = query.join(UserInGroupDB, UserInGroupDB.group_id == GroupDB.id)
    query = query.join(UserDB, UserInGroupDB.user_id == UserDB.id)
    result = []
    for group, user_in_group, user in query.all():
        result.append({
            'user': user,
            'role': user_in_group.role,
            'member_since': user_in_group.member_since_datetime
        })
    return result
