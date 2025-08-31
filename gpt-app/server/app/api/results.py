import datetime
import json
from fastapi import APIRouter, Request, HTTPException
from bson import ObjectId
from config import settings
from agent import test, MAPPOAgent
from files import fetch_model

from .requests import get_requests_collection

router = APIRouter()

def get_results_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["results"]

def result_helper(result) -> dict:
    return {
        "id": str(result["_id"]),
        "requestId": str(result.get("requestId")) if result.get("requestId") else None,
        "city": result.get("city"),
        "lanes": result.get("lanes"),
        "stops": result.get("stops", []),
        "createdAt": result.get("createdAt") or str(datetime.datetime.now()),
    }

@router.get("/{id}")
async def get_result_by_id(id: str, request: Request):
    results_collection = get_results_collection(request)
    result = results_collection.find_one({"_id": ObjectId(id)})
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"success": True, "data": result_helper(result)}

@router.get("/requests/{request_id}")
async def get_result_by_request_id(request_id: str, request: Request):
    results_collection = get_results_collection(request)
    results_cursor = results_collection.find({"requestId": ObjectId(request_id)})

    if not results_cursor:
        raise HTTPException(status_code=404, detail="Result not found")

    return {"success": True, "data": [result_helper(result) for result in results_cursor]}

@router.post("/")
async def create_result(request: Request):
    results_collection = get_results_collection(request)
    requests_collection = get_requests_collection(request)

    data = await request.json()
    request = requests_collection.find_one({"_id": ObjectId(data["requestId"])})

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    result = {}
    result["requestId"] = ObjectId(data["requestId"])
    
    for model_id in request.get("model_ids"):
        fetch_model(model_id)

    model_paths = [f"{settings.models_route}/actor_{i}.keras" for i in request.get("model_ids")]

    # Convert interestPoints to the required dict format
    interest_points_dict = {
        int(point["osm_id"]): {
            "type": point["type"],
            "grade": point["importance"], # should be grade
            "lat": float(point["lat"]),
            "lon": float(point["lon"])
        }
        for point in request["interestPoints"]
    }

    central_stations_dict = {
        int(point["osm_id"]): {
            "lat": float(point["lat"]),
            "lon": float(point["lon"])
        }
        for point in request["centralPoints"]
    }

    env = test(
        MAPPOAgent, 
        request["busCount"], 
        request["city"]["display_name"], 
        central_stations_dict, 
        interest_points_dict,
        6, 8, 
        model_paths
    )

    lanes = {}

    for i, agent_name in enumerate(env.agents):
        lane_name = f"lane_{i+1}"
        lanes[lane_name] = {
            "route": [
                {"lat": env.G.nodes[pos]['y'], "lng": env.G.nodes[pos]['x']} 
                for pos in env.trails[agent_name]
            ]
        }

    stops = [
        {"lat": env.G.nodes[station]['y'], "lng": env.G.nodes[station]['x']}
        for station in env.placed_stations
    ]

    result = {
        "stops": stops,
        "lanes": lanes,
        "city": {
            "name": request["city"]["display_name"],
            "lat": request["city"]["lat"],
            "lng": request["city"]["lon"],
        },
        "createdAt": str(datetime.datetime.now()),
        # "userId": str(request.get("userId")),
        "userId": request.get("userId"),
        # "requestId": data["requestId"]
        "requestId": ObjectId(data["requestId"])
    }

    result_inserted = results_collection.insert_one(result)
    
    return {"success": True, "data": result_helper(result)}