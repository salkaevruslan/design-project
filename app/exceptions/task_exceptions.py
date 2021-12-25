from fastapi import FastAPI
from fastapi.responses import JSONResponse


class TaskNotFoundException(Exception):
    def __init__(self, is_suggestion: bool):
        self.is_suggestion = is_suggestion


class TaskOwnerTypeNotFoundException(Exception):
    def __init__(self):
        pass


class TaskTypeException(Exception):
    def __init__(self, task_type: str):
        self.task_type = task_type


class TaskNotAssignedToYouException(Exception):
    def __init__(self):
        pass


class TaskStatusChangeException(Exception):
    def __init__(self, new_status: str):
        self.new_status = new_status


def add_task_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskNotFoundException)
    async def task_not_found_exception_handler(request, exc: TaskNotFoundException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Task {'suggestion ' if exc.is_suggestion else ''} is not found"
            },
        )

    @app.exception_handler(TaskOwnerTypeNotFoundException)
    async def task_owner_type_not_found_exception_handler(request, exc: TaskOwnerTypeNotFoundException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Task owner type not found"
            },
        )

    @app.exception_handler(TaskTypeException)
    async def task_type_exception_handler(request, exc: TaskTypeException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"This task is not a {exc.task_type} task"
            },
        )

    @app.exception_handler(TaskNotAssignedToYouException)
    async def task_not_assigned_to_you_exception_handler(request, exc: TaskNotAssignedToYouException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"This task is not assigned to you"
            },
        )

    @app.exception_handler(TaskStatusChangeException)
    async def task_status_change_exception_handler(request, exc: TaskStatusChangeException):
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Can't change task status to {exc.new_status}"
            },
        )
