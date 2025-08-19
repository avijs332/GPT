from fastapi import APIRouter, Request, HTTPException
from bson import ObjectId
from config import settings

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
        # Add more fields as needed
    }

@router.get("/requests/{request_id}")
async def get_result_by_request_id(request_id: str, request: Request):
    results_collection = get_results_collection(request)
    result = results_collection.find_one({"requestId": ObjectId(request_id)})
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"success": True, "data": result_helper(result)}
