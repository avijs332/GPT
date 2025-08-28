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

def get_feedback_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["feedback"]

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
        "hasRejectionFeedback": req.get("hasRejectionFeedback", False),
        "lastFeedbackAt": req.get("lastFeedbackAt"),
    }

@router.get("/profile/{profile_id}")
async def get_requests_by_profile(profile_id: str, request: Request):
    requests_collection = get_requests_collection(request)
    requests_cursor = requests_collection.find({"userId": ObjectId(profile_id)})
    requests = [request_helper(req) for req in requests_cursor]
    
    return {"success": True, "data": requests}

@router.get("/open")
async def get_requests_by_profile(request: Request):
    requests_collection = get_requests_collection(request)
    requests_cursor = requests_collection.find({"status": RequestStatus.pending.value})
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

@router.post("/{request_id}/reject")
async def reject_request(request_id: str, request: Request):
    """
    Handle request rejection with feedback from user
    """
    requests_collection = get_requests_collection(request)
    feedback_collection = get_feedback_collection(request)
    
    try:
        data = await request.json()
        feedback_text = data.get("feedback", "")
        
        # Validate request exists
        existing_request = requests_collection.find_one({"_id": ObjectId(request_id)})
        if not existing_request:
            return {"success": False, "error": "Request not found"}
        
        # Store feedback
        feedback_data = {
            "requestId": ObjectId(request_id),
            "feedback": feedback_text,
            "createdAt": datetime.now(),
            "userId": existing_request.get("userId")
        }
        feedback_result = feedback_collection.insert_one(feedback_data)
        
        # Optionally update request status to indicate rejection/feedback provided
        requests_collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "hasRejectionFeedback": True, 
                "lastFeedbackAt": datetime.now(), 
                "status": RequestStatus.pending.value}}
        )
        
        return {
            "success": True, 
            "message": "Feedback received successfully",
            "feedbackId": str(feedback_result.inserted_id)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/{request_id}/feedback")
async def get_request_feedback(request_id: str, request: Request):
    """
    Get all feedback for a specific request
    """
    feedback_collection = get_feedback_collection(request)
    
    try:
        feedback_cursor = feedback_collection.find({"requestId": ObjectId(request_id)})
        feedback_list = []
        
        for feedback in feedback_cursor:
            feedback_list.append({
                "id": str(feedback["_id"]),
                "requestId": str(feedback["requestId"]),
                "feedback": feedback.get("feedback", ""),
                "createdAt": feedback.get("createdAt"),
                "userId": str(feedback.get("userId")) if feedback.get("userId") else None
            })
        
        return {"success": True, "data": feedback_list}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
