from fastapi import APIRouter

from app.api.routes import authentication, users, groups, groups_admin
from app.db.db import Base, engine

Base.metadata.create_all(bind=engine)

api_router = APIRouter()
api_router.include_router(authentication.router, tags=["authentication"], prefix="/auth")
api_router.include_router(users.router, tags=["users"], prefix="/user")
api_router.include_router(groups.router, tags=["group"], prefix="/group")
api_router.include_router(groups_admin.router, tags=["admin"], prefix="/group/admin")
