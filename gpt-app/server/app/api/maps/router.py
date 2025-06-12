from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId

from config import settings

from .logic import get_routes
from gpt_types import Response, RouteRequest

maps_router = APIRouter()

def get_results_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["results"]

@maps_router.post("/predict", response_model=Response)
async def get_city_coordinates(request: RouteRequest):
    print('predicting')
    routes = get_routes(request.city_name, request.bus_count, request.interest_points, request.central_points)
 
    return {"success": True, "data": routes}

@maps_router.get("/results/{result_id}", response_model=Response)
async def get_result(result_id: str, request: Request):
    results_collection = get_results_collection(request)
    result = results_collection.find_one({"_id": ObjectId(result_id)})
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    # Remove MongoDB internal fields if needed
    result["_id"] = str(result["_id"])
    return {"success": True, "data": result}

@maps_router.get("/results/profile/{profile_id}")
async def get_results_by_profile(profile_id: str, request: Request):
    results_collection = get_results_collection(request)
    results = list(results_collection.find({"userId": profile_id}))
    for result in results:
        result["_id"] = str(result["_id"])
    return {"success": True, "data": results}

