from fastapi import APIRouter

from .logic import get_routes
from gpt_types import Response, RouteRequest

maps_router = APIRouter()

@maps_router.post("/predict", response_model=Response)
async def get_city_coordinates(request: RouteRequest):
    print('predicting')
    routes = get_routes(request.city_name, request.bus_count, request.interest_points, request.central_points)
 
    return {"success": True, "data": routes}
