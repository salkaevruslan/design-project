from fastapi import HTTPException, status

from app.db.repository.groups import delete_user_in_group_db, find_user_in_group_db
from app.db.repository.invites import get_group_invites_from_db, get_invite_by_params_db, create_invite_db
from app.db.repository.users import get_user_by_name_db
from app.models.domain.groups import Invite
from app.models.domain.users import User
from app.models.schemas.groups import InviteStatus, GroupAndUserRequest
from app.services.groups import get_group, get_invite


def get_group_as_admin(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can take this action"
        )
    return group


def get_invites_to_group(db, current_user: User, group_id: int):
    get_group_as_admin(db, current_user, group_id)
    response = get_group_invites_from_db(db, group_id)
    result = []
    for elem in response:
        user = elem['user']
        invite = elem['invite']
        result.append({
            'invite_id': invite.id,
            'datetime': invite.datetime,
            'status': invite.status,
            'user': User(id=user.id, username=user.username, email=user.email)
        })
    return result


def cancel_invite_to_group(db, current_user: User, invite_id: int):
    invite = get_invite(db, invite_id)
    group = get_group_as_admin(db, current_user, invite.group_id)
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin can modify invites to group"
        )
    if invite.status != InviteStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot cancel invite with status: {invite.status}"
        )
    db.delete(invite)
    db.commit()


def invite_user_to_group(db, current_user: User, request: GroupAndUserRequest):
    get_group_as_admin(db, current_user, request.group_id)
    invited_user = get_user_by_name_db(db, request.user_name)
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invited user not found"
        )
    if find_user_in_group_db(db, invited_user.id, request.group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )
    if get_invite_by_params_db(db, request.group_id, invited_user.id, InviteStatus.SENT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already sent"
        )
    new_invite_db = create_invite_db(db, invited_user.id, request.group_id)
    return Invite(id=new_invite_db.id,
                  group_id=new_invite_db.group_id,
                  invited_user_id=new_invite_db.user_id,
                  datetime=new_invite_db.datetime,
                  status=new_invite_db.status)


def change_group_admin(db, current_user: User, request: GroupAndUserRequest):
    group = get_group_as_admin(db, current_user, request.group_id)
    if not find_user_in_group_db(db, current_user.id, request.group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this group"
        )
    user = get_user_by_name_db(db, request.user_name)
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yau are already admin of this group"
        )
    db.commit()
    db.refresh(group)


def kick_user_from_group(db, current_user: User, request: GroupAndUserRequest):
    group = get_group_as_admin(db, current_user, request.group_id)
    if not find_user_in_group_db(db, current_user.id, request.group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a member of this group"
        )
    user = get_user_by_name_db(db, request.user_name)
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yau cannot kick yourself"
        )
    delete_user_in_group_db(db, user.id, group.id)
