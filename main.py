from fastapi import FastAPI
from app.api.api import api_router
from app.exceptions.handlers import add_exception_handlers

app = FastAPI()

app.include_router(api_router)
add_exception_handlers(app)
