from fastapi import HTTPException, status

from app.db.repository.groups import create_user_in_group_db
from app.db.repository.invites import get_user_invites_from_db
from app.models.domain.groups import Group
from app.models.domain.users import User
from app.models.enums.invite import InviteStatus
from app.services.groups import get_invite


def get_my_invites_to_groups(db, current_user: User):
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
        create_user_in_group_db(db, invite.user_id, invite.group_id)
    db.commit()
    db.refresh(invite)
