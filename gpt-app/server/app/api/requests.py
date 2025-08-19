from enum import Enum
from bson import ObjectId
from fastapi import APIRouter, Request
from config import settings
from datetime import datetime

class RequestStatus(str, Enum):
    pending = 'pending'
    finished = 'finished'

router = APIRouter()

def get_requests_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["requests"]

def request_helper(req) -> dict:
    return {
        "id": str(req["_id"]),
        "city": req.get("city"),
        "busCount": req.get("busCount"),
        "interestPoints": req.get("interestPoints", []),
        "centralStations": req.get("centralStations", []),
        "status": req.get("status"),
        "userId": str(req.get("userId")) if req.get("userId") else None,
        "createdAt": req.get("createdAt"),
    }

@router.get("/profile/{profile_id}")
async def get_requests_by_profile(profile_id: str, request: Request):
    requests_collection = get_requests_collection(request)
    requests_cursor = requests_collection.find({"userId": ObjectId(profile_id)})
    requests = [request_helper(req) for req in requests_cursor]
    
    return {"success": True, "data": requests}

@router.post("/")
async def create_request(request: Request):
    requests_collection = get_requests_collection(request)
    data = await request.json()
    # Default status to pending if not provided
    if "status" not in data or data["status"] not in [e.value for e in RequestStatus]:
        data["status"] = RequestStatus.pending.value
    data["createdAt"] = datetime.now()
    data["userId"] = ObjectId(data["userId"])   
    result = requests_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    data = request_helper(data)

    return {"success": True, "data": data}
