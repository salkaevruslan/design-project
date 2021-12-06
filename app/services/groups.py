from fastapi import HTTPException, status
from app.db.repository.groups import get_user_groups_from_db, get_users_in_group_from_db, get_group_by_id_db, \
    create_group_db, create_user_in_group_db
from app.db.repository.invites import get_user_invites_from_db, get_group_invites_from_db, get_invite_by_id_db, \
    get_invite_by_params_db, create_invite_db
from app.db.repository.users import get_user_by_name_db, get_user_by_id_db
from app.models.domain.groups import Group, Invite
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest, InviteStatus
from app.models.schemas.groups import InviteCreationRequest


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
    response = get_users_in_group_from_db(db, group_id)
    if not any(current_user.id == elem['user'].id for elem in response):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yau are not a member of this group"
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
    invited_user = get_user_by_name_db(db, request.invited_user_name)
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


def get_invite(db, invite_id: int):
    invite = get_invite_by_id_db(db, invite_id)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite not found"
        )
    return invite


def cancel_invite(db, current_user: User, invite_id: int):
    invite = get_invite(db, invite_id)
    group = get_group(db, invite.group_id)
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


def process_invite(db, current_user: User, invite_id: int, is_accept: bool):
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
        create_user_in_group_db(db, invite.user_id, invite.group_id)
    db.commit()
    db.refresh(invite)


def get_my_invites(db, current_user: User):
    response = get_user_invites_from_db(db, current_user.id)
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
                           admin=User(id=admin.id,
                                      username=admin.username,
                                      email=admin.email)
                           ),
        })
    return result


def get_list_of_invites_to_group(db, current_user: User, group_id: int):
    group = get_group(db, group_id)
    if group.admin_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only admin can view group invitation"
        )
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
