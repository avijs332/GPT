import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from auth import auth_router
from api import api_router
from config import lifespan, settings
from jwt_token import decode_token

app = FastAPI(lifespan=lifespan) # uvicorn main:app --reload

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
            token = auth_header.split(" ", 1)[1]
            try:
                decode_token(token)
            except Exception as e:
                return JSONResponse(status_code=401, content={"detail": str(e)})
        response = await call_next(request)
        return response

app.add_middleware(AuthMiddleware)

app.include_router(auth_router, tags=["auth"], prefix="/auth")
app.include_router(api_router, tags=["api"], prefix="/api")

# app.mount("/static", StaticFiles(directory="./dist"), name="static")

# @app.get("/{full_path:path}")
# async def serve_react_app(full_path: str):
#     path = "./dist/"

#     if (full_path == ''):
#         path += 'index.html'
#     else:
#         path += full_path

#     if os.path.exists(path):
#         return FileResponse(path)
#     return {"error": f"{path} not found"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.environment == "development",
        port=settings.PORT,
    )
