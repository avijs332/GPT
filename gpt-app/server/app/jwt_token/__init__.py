import datetime
from fastapi import HTTPException
import jwt
from config import settings


def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

__all__ = ["create_token", "decode_token"]