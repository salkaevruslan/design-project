from fastapi import HTTPException, status

import app.db.repository.groups as groups_repository
import app.db.repository.invites as invites_repository
from app.db.repository.users import get_user_by_name_db
from app.services.models.groups import Group
from app.services.models.invite import Invite
from app.services.models.users import User
from app.models.enums.invite import InviteStatus
from app.api.models.groups import GroupAndUserRequest
from app.services.groups_admin import get_group_as_admin


def get_invite(db, invite_id: int):
    invite = invites_repository.get_invite_by_id_db(db, invite_id)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite not found"
        )
    return invite


def get_my_invites_to_groups(db, current_user: User):
    response = invites_repository.get_user_invites_from_db(db, current_user.id)
    result = []
    for elem in response:
        group = elem['group']
        admin = elem['admin']
        invite = elem['invite']
        result.append({
            'invite_id': invite.id,
            'datetime': invite.datetime,
            'status': invite.status,
            'group': Group(id=group.id,
                           name=group.name,
                           creation_datetime=group.creation_datetime,
                           admin=User(id=admin.id,
                                      username=admin.username,
                                      email=admin.email)
                           ),
        })
    return result


def process_invite_to_group(db, current_user: User, invite_id: int, is_accept: bool):
    invite = get_invite(db, invite_id)
    if invite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot {'accept' if is_accept else 'decline'} this invite"
        )
    if invite.status != InviteStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You cannot {'accept' if is_accept else 'decline'} invite with status: {invite.status}"
        )
    invite.status = InviteStatus.ACCEPTED if is_accept else InviteStatus.DECLINED
    if is_accept:
        groups_repository.create_user_in_group_db(db, invite.user_id, invite.group_id)
    db.commit()
    db.refresh(invite)


def get_invites_to_group(db, current_user: User, group_id: int):
    get_group_as_admin(db, current_user, group_id)
    response = invites_repository.get_group_invites_from_db(db, group_id)
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
    get_group_as_admin(db, current_user, invite.group_id)
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
    if groups_repository.get_user_in_group_db(db, invited_user.id, request.group_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )
    if invites_repository.get_invite_by_params_db(db, request.group_id, invited_user.id, InviteStatus.SENT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already sent"
        )
    new_invite_db = invites_repository.create_invite_db(db, invited_user.id, request.group_id)
    return Invite(id=new_invite_db.id,
                  group_id=new_invite_db.group_id,
                  invited_user_id=new_invite_db.user_id,
                  datetime=new_invite_db.datetime,
                  status=new_invite_db.status)
