from fastapi import HTTPException, status

import app.db.repository.groups as groups_repository
import app.db.repository.users as users_repository
from app.services.models.users import User
from app.models.enums.groups import GroupRole
from app.api.models.groups import GroupAndUserRequest
from app.services.groups import get_group


def get_group_as_admin(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    admin_in_group = groups_repository.get_admin_in_group_db(db, group_id)
    if admin_in_group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not admin of this group"
        )
    return group


def change_group_admin(db, current_user: User, request: GroupAndUserRequest):
    get_group_as_admin(db, current_user, request.group_id)
    new_admin_user = users_repository.get_user_by_name_db(db, request.user_name)
    if not new_admin_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    if current_user.id == new_admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already admin of this group"
        )
    new_admin_in_group = groups_repository.get_user_in_group_db(db, new_admin_user.id, request.group_id)
    current_user_in_group = groups_repository.get_user_in_group_db(db, current_user.id, request.group_id)
    if not new_admin_in_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this group"
        )
    new_admin_in_group.role = GroupRole.ADMIN
    current_user_in_group.role = GroupRole.MEMBER
    db.commit()
    db.refresh(current_user_in_group)
    db.refresh(new_admin_in_group)


def kick_user_from_group(db, current_user: User, request: GroupAndUserRequest):
    group = get_group_as_admin(db, current_user, request.group_id)
    user = users_repository.get_user_by_name_db(db, request.user_name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    if not groups_repository.get_user_in_group_db(db, user.id, request.group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this group"
        )
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yau cannot kick yourself"
        )
    groups_repository.delete_user_in_group_db(db, user.id, group.id)


def delete_group(db, current_user: User, group_id: int):
    group = get_group_as_admin(db, current_user, group_id)
    members = groups_repository.get_users_in_group_from_db(db, group_id)
    for member_info in members:
        user_in_group = groups_repository.get_user_in_group_db(db, member_info['user'].id, group_id)
        db.delete(user_in_group)
    db.commit()
    db.delete(group)
    db.commit()
