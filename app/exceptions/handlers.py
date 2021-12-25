from fastapi import FastAPI

from app.exceptions.group_exceptions import add_group_exception_handlers
from app.exceptions.invite_exceptions import add_invite_exception_handlers
from app.exceptions.task_exceptions import add_task_exception_handlers
from app.exceptions.user_exceptions import add_user_exception_handlers


def add_exception_handlers(app: FastAPI) -> None:
    add_user_exception_handlers(app)
    add_group_exception_handlers(app)
    add_invite_exception_handlers(app)
    add_task_exception_handlers(app)
