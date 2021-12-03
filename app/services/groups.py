from fastapi import HTTPException, status
from app.db.models.groups import UserInGroupDB, GroupDB, InviteDB
from app.db.models.users import UserDB
from app.models.domain.groups import Group, Invite
from app.models.domain.users import User
from app.models.schemas.groups import GroupCreationRequest, InviteStatus
from app.models.schemas.groups import InviteCreationRequest
from app.services.authentication import get_user_from_db


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


def get_user_groups(db, user: User):
    groups = get_user_groups_from_db(db, user.username)
    result = []
    for group in groups:
        result.append(Group(id=group.id, name=group.name, admin_id=group.admin_id))
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
    if get_invite_by_params_db(db, request.group_id, invited_user.id, InviteStatus.SENT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already sent"
        )
    new_invite_db = InviteDB(user_id=invited_user.id, group_id=request.group_id)
    db.add(new_invite_db)
    db.commit()
    db.refresh(new_invite_db)
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
        user_in_group = UserInGroupDB(user_id=current_user.id, group_id=invite.group_id)
        db.add(user_in_group)
        db.commit()
        db.refresh(invite)
        db.refresh(user_in_group)
    else:
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
            'group': Group(id=group.id, name=group.name, admin_id=group.admin_id),
            'admin': User(id=admin.id, username=admin.username, email=admin.email),
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


def get_invite_by_params_db(db, group_id: int, user_id: int, invite_status: InviteStatus):
    query = db.query(InviteDB)
    query = query.filter(InviteDB.user_id == user_id)
    query = query.filter(InviteDB.group_id == group_id)
    query = query.filter(InviteDB.status == invite_status)
    return query.all()


def get_invite_by_id_db(db, invite_id: int):
    return db.query(InviteDB).filter(InviteDB.id == invite_id).first()


def get_user_invites_from_db(db, user_id: int):
    query = db.query(InviteDB, GroupDB, UserDB)
    query = query.filter(InviteDB.user_id == user_id)
    query = query.join(GroupDB, InviteDB.group_id == GroupDB.id)
    query = query.join(UserDB, GroupDB.admin_id == UserDB.id)
    result = []
    for invite, group, user in query.all():
        result.append({
            'invite': invite,
            'group': group,
            'admin': user,
        })
    return result


def get_group_invites_from_db(db, group_id: int):
    query = db.query(InviteDB, UserDB)
    query = query.filter(InviteDB.group_id == group_id)
    query = query.join(UserDB, InviteDB.user_id == UserDB.id)
    result = []
    for invite, user in query.all():
        result.append({
            'invite': invite,
            'user': user,
        })
    return result


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
        result.append({
            'user': user,
            'member_since': user_in_group.member_since_datetime
        })
    return result
