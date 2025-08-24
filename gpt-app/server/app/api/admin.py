from fastapi import APIRouter, UploadFile, File, Form
from files.utils import save_model_to_db
from pymongo import MongoClient
from bson import ObjectId
from config import settings

router = APIRouter()

client = MongoClient(settings.db_uri)
db = client[settings.db_name]

@router.post('/upload-model/')
async def upload_model(request_id: str = Form(...), file: UploadFile = File(...)):
    doc_id = save_model_to_db(file.file, file.filename)
    # Associate the uploaded model with the request entity
    db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$push": {"model_ids": doc_id}}
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