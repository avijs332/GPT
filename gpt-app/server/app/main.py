import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from logic import get_routes
from gpt_types import Response, RouteRequest

app = FastAPI() # uvicorn main:app --reload

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict", response_model=Response)
async def get_city_coordinates(request: RouteRequest):
    routes = get_routes(request.city_name, request.bus_count, request.interest_points, request.central_points)
 
    return {"success": True, "data": routes}

app.mount("/static", StaticFiles(directory="./dist"), name="static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    path = "./dist/"

    print(full_path)

    if (full_path == ''):
        path += 'index.html'
    else:
        path += full_path

    if os.path.exists(path):
        return FileResponse(path)
    return {"error": f"{path} not found"}
