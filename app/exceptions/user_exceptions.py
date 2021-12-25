from fastapi import FastAPI
from fastapi.responses import JSONResponse


class UserNotFoundException(Exception):
    def __init__(self, name: str):
        self.name = name


class UserAlreadyExistsException(Exception):
    def __init__(self, is_name: bool):
        self.is_name = is_name


def add_user_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundException)
    async def user_not_found_exception_handler(request, exc: UserNotFoundException):
        return JSONResponse(
            status_code=400,
            content={"message": f"User not found with name: {exc.name}"},
        )

    @app.exception_handler(UserNotFoundException)
    async def user_already_exists_handler(request, exc: UserAlreadyExistsException):
        return JSONResponse(
            status_code=400,
            content={"message": f"User with this {'name' if exc.is_name else 'email'} already exists"},
        )

