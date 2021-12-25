from fastapi import FastAPI
from fastapi.responses import JSONResponse


class InviteProcessingException(Exception):
    def __init__(self, process_type: str):
        self.process_type = process_type


class InviteAlreadySentException(Exception):
    def __init__(self):
        pass


class InviteNotFoundException(Exception):
    def __init__(self):
        pass


def add_invite_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InviteProcessingException)
    async def invite_process_exception_handler(request, exc: InviteProcessingException):
        return JSONResponse(
            status_code=400,
            content={"message": f"You cannot {exc.process_type} this invite"},
        )

    @app.exception_handler(InviteAlreadySentException)
    async def invite_process_exception_handler(request, exc: InviteAlreadySentException):
        return JSONResponse(
            status_code=400,
            content={"message": f"Invite already sent"},
        )

    @app.exception_handler(InviteAlreadySentException)
    async def invite_not_found_handler(request, exc: InviteNotFoundException):
        return JSONResponse(
            status_code=400,
            content={"message": f"Invite not found"},
        )
