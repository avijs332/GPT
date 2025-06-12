from fastapi import APIRouter
from .maps import maps_router
from .users import router as users_router
from .requests import router as requests_router
from .results import router as results_router

api_router = APIRouter()

api_router.include_router(maps_router, tags=["maps"], prefix="/maps")
api_router.include_router(users_router, tags=["users"], prefix="/users")
api_router.include_router(requests_router, tags=["requests"], prefix="/requests")
api_router.include_router(results_router, tags=["results"], prefix="/results")

__all__ = ["api_router"]