import app.db.repository.groups as groups_repository
import app.db.repository.users as users_repository
from app.exceptions import user_exceptions, group_exceptions
from app.services.models.users import User
from app.models.enums.groups import GroupRole
from app.services.groups import get_group


def get_group_as_admin(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    admin_in_group = groups_repository.get_admin_in_group_db(db, group_id)
    if admin_in_group.user_id != current_user.id:
        raise group_exceptions.GroupOwnershipLeaveException(is_you=True, is_admin=False)
    return group


def change_group_admin(db, current_user: User, group_id: int, new_admin_name: str):
    get_group_as_admin(db, current_user, group_id)
    new_admin_user = users_repository.get_user_by_name_db(db, new_admin_name)
    if not new_admin_user:
        raise user_exceptions.UserNotFoundException(name=new_admin_user)
    if current_user.id == new_admin_user.id:
        raise group_exceptions.GroupOwnershipLeaveException(is_you=True, is_admin=True)
    new_admin_in_group = groups_repository.get_user_in_group_db(db, new_admin_user.id, group_id)
    current_user_in_group = groups_repository.get_user_in_group_db(db, current_user.id, group_id)
    if not new_admin_in_group:
        raise group_exceptions.GroupMembershipException(is_you=False, is_member=False)
    new_admin_in_group.role = GroupRole.ADMIN
    current_user_in_group.role = GroupRole.MEMBER
    db.commit()
    db.refresh(current_user_in_group)
    db.refresh(new_admin_in_group)


def kick_user_from_group(db, current_user: User, group_id: int, user_name: str):
    group = get_group_as_admin(db, current_user, group_id)
    user = users_repository.get_user_by_name_db(db, user_name)
    if not user:
        raise user_exceptions.UserNotFoundException(name=user_name)
    if not groups_repository.get_user_in_group_db(db, user.id, group_id):
        raise group_exceptions.GroupMembershipException(is_you=False, is_member=False)
    if current_user.id == user.id:
        raise group_exceptions.GroupKickException()
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
