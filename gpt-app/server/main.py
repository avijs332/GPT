from fastapi import FastAPI
from pydantic import BaseModel
import random  # Replace this with your DeepRL model

app = FastAPI()

# Input Schema
class RequestData(BaseModel):
    city_name: str
    num_buses: int

# Fake route generation (Replace with your RL model)
def generate_routes(city_name: str, num_buses: int):
    return {"city": city_name, "routes": [f"Route {i+1}" for i in range(num_buses)]}

@app.post("/generate_routes")
def generate_bus_routes(data: RequestData):
    routes = generate_routes(data.city_name, data.num_buses)
    return {"success": True, "data": routes}

# Run with: uvicorn main:app --reload
