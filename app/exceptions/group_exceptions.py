from fastapi import FastAPI
from fastapi.responses import JSONResponse


class GroupMembershipException(Exception):
    def __init__(self, is_you: bool, is_member: bool):
        self.is_you = is_you
        self.is_member = is_member


class GroupNotFoundException(Exception):
    def __init__(self):
        pass


class GroupAdminLeaveException(Exception):
    def __init__(self):
        pass


class GroupOwnershipLeaveException(Exception):
    def __init__(self, is_you: bool, is_admin: bool):
        self.is_you = is_you
        self.is_admin = is_admin


class GroupKickException(Exception):
    def __init__(self):
        pass


def add_group_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GroupMembershipException)
    async def group_membership_exception_handler(request, exc: GroupMembershipException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"{'You are' if exc.is_you else 'User is'}"
                           f" {'already' if exc.is_member else 'not'} a member of this group"
            },
        )

    @app.exception_handler(GroupOwnershipLeaveException)
    async def group_ownership_exception_handler(request, exc: GroupOwnershipLeaveException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"{'You are' if exc.is_you else 'User is'}"
                           f" {'already' if exc.is_admin else 'not'} an admin of this group"
            },
        )

    @app.exception_handler(GroupNotFoundException)
    async def group_not_found_exception_handler(request, exc: GroupNotFoundException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Group not found"
            },
        )

    @app.exception_handler(GroupAdminLeaveException)
    async def group_admin_leave_exception_handler(request, exc: GroupAdminLeaveException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"You need to make another member admin, before leaving this group"
            },
        )

    @app.exception_handler(GroupKickException)
    async def group_kick_exception_handler(request, exc: GroupKickException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"You cannot kick yourself"
            },
        )
