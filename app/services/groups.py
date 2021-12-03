from fastapi import HTTPException, status
from app.db.models.groups import UserInGroupDB, GroupDB, InviteDB
from app.db.models.users import UserDB
from app.models.domain.groups import Group, Invite
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest
from app.models.schemas.groups import InviteCreationRequest
from app.services.authentication import get_user_from_db


def get_user_groups(db, user: User):
    groups = get_user_groups_from_db(db, user.username)
    result = []
    for group in groups:
        result.append(Group(id=group.id, name=group.name, admin_id=group.admin_id))
    return result


def create_group(db, user: User, request: GroupCreationRequest):
    new_db_group = GroupDB(name=request.name, admin_id=user.id)
    db.add(new_db_group)
    db.commit()
    db.refresh(new_db_group)
    admin_in_group = UserInGroupDB(user_id=user.id, group_id=new_db_group.id)
    db.add(admin_in_group)
    db.commit()
    db.refresh(admin_in_group)
    return Group(id=new_db_group.id, name=new_db_group.name, admin_id=new_db_group.admin_id)


def get_group(db, group_id: int):
    group = get_group_from_db(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group not found"
        )
    return group


def get_group_members(db, current_user: User, group_id: int):
    get_group(db, group_id)
    response = get_users_in_group_from_db(db, group_id)
    if not any(current_user.id == elem['user'].id for elem in response):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this group"
        )
    result = []
    for elem in response:
        member = elem['user']
        result.append(
            {
                'user': User(id=member.id, username=member.username, email=member.email),
                'member_since': elem['member_since']
            }
        )
    return result


def invite_user_to_group(db, current_user: User, request: InviteCreationRequest):
    invited_user = get_user_from_db(db, request.invited_user_name)
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invited user not found"
        )
    group = get_group(db, request.group_id)
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can invite user to group"
        )
    if any(group.id == request.group_id for group in get_user_groups_from_db(db, request.invited_user_name)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )
    new_invite_db = InviteDB(user_id=invited_user.id, group_id=request.group_id)
    db.add(new_invite_db)
    db.commit()
    db.refresh(new_invite_db)
    return Invite(group_id=new_invite_db.group_id,
                  invited_user_id=new_invite_db.user_id,
                  datetime=new_invite_db.datetime)


def get_group_from_db(db, group_id: int):
    return db.query(GroupDB).filter(GroupDB.id == group_id).first()


def get_user_groups_from_db(db, username: str):
    query = db.query(UserDB, UserInGroupDB, GroupDB)
    query = query.filter(UserDB.username == username)
    query = query.join(UserInGroupDB, UserInGroupDB.user_id == UserDB.id)
    query = query.join(GroupDB, UserInGroupDB.group_id == GroupDB.id)
    result = []
    for user, user_in_group, group in query.all():
        result.append(group)
    return result


def get_users_in_group_from_db(db, group_id: int):
    query = db.query(GroupDB, UserInGroupDB, UserDB)
    query = query.filter(GroupDB.id == group_id)
    query = query.join(UserInGroupDB, UserInGroupDB.group_id == GroupDB.id)
    query = query.join(UserDB, UserInGroupDB.user_id == UserDB.id)
    result = []
    for group, user_in_group, user in query.all():
        result.append({'user': user, 'member_since': user_in_group.member_since_datetime})
    return result
