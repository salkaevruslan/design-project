from fastapi import HTTPException, status
import app.db.repository.groups as groups_repository
import app.db.repository.users as users_repository
from app.services.models.groups import Group
from app.services.models.users import User
from app.models.enums.groups import GroupRole
from app.api.models.groups import GroupCreationRequest


def create_group(db, user: User, request: GroupCreationRequest):
    new_db_group = groups_repository.create_group_db(db, request.name)
    groups_repository.create_user_in_group_db(db, user.id, new_db_group.id, GroupRole.ADMIN)
    return Group(id=new_db_group.id,
                 name=new_db_group.name,
                 admin=user,
                 creation_datetime=new_db_group.creation_datetime
                 )


def get_group(db, group_id: int):
    group = groups_repository.get_group_by_id_db(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group not found"
        )
    return group


def get_group_as_member(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    if not groups_repository.get_user_in_group_db(db, current_user.id, group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group"
        )
    return group


def get_user_groups(db, current_user: User):
    groups_info = groups_repository.get_user_groups_from_db(db, current_user.id)
    response = []
    for elem in groups_info:
        group = elem['group']
        admin_in_group = groups_repository.get_admin_in_group_db(db, group.id)
        admin = users_repository.get_user_by_id_db(db, admin_in_group.user_id)
        response.append({'group': Group(id=group.id,
                                        name=group.name,
                                        creation_datetime=group.creation_datetime,
                                        admin=User(id=admin.id,
                                                   username=admin.username,
                                                   email=admin.email)
                                        ),
                         'role': elem['role']
                         })
    return response


def get_group_members(db, current_user: User, group_id: int):
    get_group_as_member(db, current_user, group_id)
    response = groups_repository.get_users_in_group_from_db(db, group_id)
    result = []
    for elem in response:
        member = elem['user']
        result.append(
            {
                'user': User(id=member.id, username=member.username, email=member.email),
                'role': elem['role'],
                'member_since': elem['member_since']
            }
        )
    return result


def leave_from_group(db, current_user: User, group_id: int):
    get_group_as_member(db, current_user, group_id)
    admin_in_group = groups_repository.get_admin_in_group_db(db, group_id)
    if admin_in_group.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to make another member admin, before leaving this group"
        )
    groups_repository.delete_user_in_group_db(db, current_user.id, group_id)
