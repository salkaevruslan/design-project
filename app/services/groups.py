from app.db.models.groups import UserInGroupDB, GroupDB
from app.db.models.users import UserDB
from app.models.domain.groups import Group
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest


def get_user_groups(db, user: User):
    groups = get_user_groups_from_db(db, user.username)
    result = []
    for group in groups:
        result.append(Group(id=group.id, name=group.name))
    return result


def create_group(db, user: User, group: GroupCreationRequest):
    new_db_group = GroupDB(name=group.name, admin_id=user.id)
    db.add(new_db_group)
    db.commit()
    db.refresh(new_db_group)
    return new_db_group


def get_user_groups_from_db(db, username: str):
    query = db.query(UserDB).filter(UserDB.username == username)
    query = query.join(UserInGroupDB, UserInGroupDB.user_id == UserDB.id)
    query = query.join(GroupDB, UserInGroupDB.group_id == GroupDB.id)
    result = []
    for user, user_in_group, group in query.all():
        result.append(group)
    return result


def get_users_in_group_from_db(db, group_id: int):
    query = db.query(GroupDB).filter(GroupDB.id == group_id)
    query = query.join(UserInGroupDB, UserInGroupDB.group_id == GroupDB.id)
    query = query.join(UserDB, UserInGroupDB.user_id == UserDB.id)
    result = []
    for group, user_in_group, user in query.all():
        result.append(user)
    return result
