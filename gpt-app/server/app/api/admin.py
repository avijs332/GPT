from fastapi import APIRouter, UploadFile, File, Form
from files.utils import save_model_to_db
from pymongo import MongoClient
from bson import ObjectId
from config import settings
from datetime import datetime

router = APIRouter()

client = MongoClient(settings.db_uri)
db = client[settings.db_name]

@router.post('/upload-model/')
async def upload_model(request_id: str = Form(...), file: UploadFile = File(...)):
    doc_id = save_model_to_db(file.file, file.filename)
    
    # Associate the uploaded model with the request entity
    db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$push": {"model_ids": doc_id},
            "$set": {"lastModelUploadAt": datetime.now()}
        }
    )
    
    return {"doc_id": str(doc_id)}

@router.put('/requests/complete/{request_id}/')
def complete_request(request_id: str):
    result = db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "finished"}}
    )
    if result.modified_count:
        return {"success": True, "message": "Request marked as complete."}
    else:
        return {"success": False, "message": "Request not found or already complete."}

@router.get('/models')
async def get_all_models():
    """
    Get all uploaded models with metadata from GridFS and request references
    """
    try:
        # Get all requests with model_ids
        requests_collection = db.requests
        requests_cursor = requests_collection.find({"model_ids": {"$exists": True, "$ne": []}})
        
        # Get all models from GridFS fs.files collection
        fs_files_collection = db.fs.files
        
        models = []
        
        for request in requests_cursor:
            request_id = str(request["_id"])
            model_ids = request.get("model_ids", [])
            
            for model_id in model_ids:
                # Get model metadata from fs.files
                model_file = fs_files_collection.find_one({"_id": ObjectId(model_id)})
                if model_file:
                    models.append({
                        "id": str(model_file["_id"]),
                        "filename": model_file.get("filename", "Unknown"),
                        "requestId": request_id,
                        "uploadedAt": model_file.get("uploadDate", model_file.get("createdAt")),
                        "size": model_file.get("length")  # GridFS uses 'length' for file size
                    })
        
        return {"success": True, "data": models}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get('/models/request/{request_id}')
async def get_models_for_request(request_id: str):
    """
    Get all models associated with a specific request
    """
    try:
        # Get the request with its model_ids
        request = db.requests.find_one({"_id": ObjectId(request_id)})
        if not request:
            return {"success": False, "error": "Request not found"}
        
        model_ids = request.get("model_ids", [])
        if not model_ids:
            return {"success": True, "data": []}
        
        # Get model metadata from GridFS fs.files collection
        fs_files_collection = db.fs.files
        models = []
        
        for model_id in model_ids:
            model_file = fs_files_collection.find_one({"_id": ObjectId(model_id)})
            if model_file:
                models.append({
                    "id": str(model_file["_id"]),
                    "filename": model_file.get("filename", "Unknown"),
                    "requestId": request_id,
                    "uploadedAt": model_file.get("uploadDate", model_file.get("createdAt")),
                    "size": model_file.get("length")
                })
        
        return {"success": True, "data": models}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.delete('/models/{model_id}')
async def delete_model(model_id: str):
    """
    Delete a model by ID from GridFS and remove references from requests
    """
    try:
        # Delete from GridFS (both fs.files and fs.chunks)
        fs_files_collection = db.fs.files
        fs_chunks_collection = db.fs.chunks
        
        # Check if model exists
        model_file = fs_files_collection.find_one({"_id": ObjectId(model_id)})
        if not model_file:
            return {"success": False, "error": "Model not found"}
        
        # Delete from fs.files
        fs_files_collection.delete_one({"_id": ObjectId(model_id)})
        
        # Delete associated chunks from fs.chunks
        fs_chunks_collection.delete_many({"files_id": ObjectId(model_id)})
        
        # Remove reference from requests collection
        db.requests.update_many(
            {},
            {"$pull": {"model_ids": ObjectId(model_id)}}
        )
        
        return {"success": True, "message": "Model deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get('/feedbacks')
async def get_all_feedbacks():
    """
    Get all user feedbacks
    """
    try:
        feedback_collection = db.feedback
        feedback_cursor = feedback_collection.find().sort("createdAt", -1)  # Sort by newest first
        feedbacks = []
        
        for feedback in feedback_cursor:
            feedbacks.append({
                "id": str(feedback["_id"]),
                "requestId": str(feedback["requestId"]),
                "feedback": feedback.get("feedback", ""),
                "createdAt": feedback.get("createdAt"),
                "userId": str(feedback.get("userId")) if feedback.get("userId") else None
            })
        
        return {"success": True, "data": feedbacks}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get('/feedbacks/request/{request_id}')
async def get_request_feedbacks(request_id: str):
    """
    Get feedbacks for a specific request
    """
    try:
        feedback_collection = db.feedback
        feedback_cursor = feedback_collection.find({"requestId": ObjectId(request_id)}).sort("createdAt", -1)
        feedbacks = []
        
        for feedback in feedback_cursor:
            feedbacks.append({
                "id": str(feedback["_id"]),
                "requestId": str(feedback["requestId"]),
                "feedback": feedback.get("feedback", ""),
                "createdAt": feedback.get("createdAt"),
                "userId": str(feedback.get("userId")) if feedback.get("userId") else None
            })
        
        return {"success": True, "data": feedbacks}
    except Exception as e:
        return {"success": False, "error": str(e)}