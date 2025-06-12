from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId

from config import settings

router = APIRouter()

def get_users_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["users"]

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "joinedAt": user.get("joinedAt"),
        # Do not expose password
    }

@router.get("", response_model=list[dict])
def get_users(users_collection=Depends(get_users_collection)):
    users = []
    for user in users_collection.find():
        users.append(user_helper(user))
    return users

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str, users_collection=Depends(get_users_collection)):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    raise HTTPException(status_code=404, detail="User not found")
