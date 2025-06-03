from fastapi import APIRouter
from .maps import maps_router
from .users import router as users_router

api_router = APIRouter()

api_router.include_router(maps_router, tags=["maps"], prefix="/maps")
api_router.include_router(users_router, tags=["users"], prefix="/users")

__all__ = ["api_router"]