from fastapi import APIRouter, Depends, HTTPException, Request, Header
from bson import ObjectId
import hashlib
from datetime import datetime

from jwt_token import create_token, decode_token
from config import settings

from .auth_types import LoginRequest, RegisterRequest

auth_router = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_users_collection(request: Request):
    client = request.app.state.mongo_client
    if client is None:
        raise RuntimeError("mongo_client is not initialized. Check your database configuration.")
    db = client[settings.db_name]
    return db["users"]

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "username": user.get("username"),
        "email": user.get("email"),
        "joinedAt": user.get("joinedAt"),
        # Do not expose password
    }

@auth_router.post("/login")
def login(data: LoginRequest, users_collection=Depends(get_users_collection)):
    users = users_collection
    user = users.find_one({"username": data.username})
    if not user or user.get("password") != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(str(user["_id"]))
    return {"user": user_helper(user), "token": token}

@auth_router.post("/register")
def register(data: RegisterRequest, users_collection=Depends(get_users_collection)):
    users = users_collection
    if users.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_data = {
        "name": data.name,
        "username": data.username,
        "email": data.email,
        "password": hash_password(data.password),
        "joinedAt": datetime.now()
    }
    result = users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    token = create_token(str(user_data["_id"]))
    return {"user": user_helper(user_data), "token": token}

@auth_router.get("/me")
def me(Authorization: str = Header(...), users_collection=Depends(get_users_collection)):
    # Expect header: Authorization: Bearer <token>
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = Authorization.split(" ", 1)[1]
    user_id = decode_token(token)
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)