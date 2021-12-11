from fastapi import HTTPException, status
from app.db.repository.groups import get_user_groups_from_db, get_users_in_group_from_db, get_group_by_id_db, \
    create_group_db, create_user_in_group_db, delete_user_in_group_db, find_user_in_group_db
from app.db.repository.invites import get_user_invites_from_db, get_invite_by_id_db
from app.db.repository.users import get_user_by_id_db
from app.models.domain.groups import Group
from app.models.domain.users import User
from app.models.enums.invite import InviteStatus
from app.models.schemas.groups import GroupCreationRequest


def create_group(db, user: User, request: GroupCreationRequest):
    new_db_group = create_group_db(db, user.id, request.name)
    create_user_in_group_db(db, user.id, new_db_group.id)
    return Group(id=new_db_group.id, name=new_db_group.name, admin=user)


def get_group(db, group_id: int):
    group = get_group_by_id_db(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group not found"
        )
    return group


def get_invite(db, invite_id: int):
    invite = get_invite_by_id_db(db, invite_id)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite not found"
        )
    return invite


def get_user_groups(db, user: User):
    groups = get_user_groups_from_db(db, user.username)
    result = []
    for group in groups:
        admin = get_user_by_id_db(db, group.admin_id)
        result.append(Group(id=group.id,
                            name=group.name,
                            admin=User(id=admin.id,
                                       username=admin.username,
                                       email=admin.email)
                            )
                      )
    return result


def get_group_members(db, current_user: User, group_id: int):
    get_group(db, group_id)
    if not find_user_in_group_db(db, current_user.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group"
        )
    response = get_users_in_group_from_db(db, group_id)
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


def leave_from_group(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    if not find_user_in_group_db(db, current_user.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group"
        )
    if group.admin_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to make other member admin, before leaving this group"
        )
    delete_user_in_group_db(db, current_user.id, group_id)
