from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import osmnx as ox
from logic import get_routes

app = FastAPI() # uvicorn main:app --reload

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OsmLocation(BaseModel):
    place_id: int
    licence: str
    osm_type: str
    osm_id: int
    lat: float
    lon: float
    # class_: str  # 'class' is a reserved keyword in Python
    # type: str
    place_rank: int
    importance: float
    addresstype: str
    name: str
    display_name: str
    boundingbox: Tuple[float, float, float, float]

    class Config:
        frozen = True  # Makes it hashable
    #     fields = {'class_': 'class'}

class RouteRequest(BaseModel):
    city_name: Optional[str] = None
    bus_count: Optional[int] = None
    interest_points: Optional[List[OsmLocation]] = None
    central_points: Optional[List[OsmLocation]] = None


class Coordinate(BaseModel):
    lat: float
    lng: float


class RouteResponse(BaseModel):
    success: bool
    route: List[Coordinate]


from typing import List, Dict, TypedDict


class Lane(BaseModel):
    stops: List[Coordinate]
    route: List[Coordinate]


class Data(BaseModel):
    city: Coordinate
    lanes: Dict[str, Lane]


class Response(BaseModel):
    success: bool
    data: Data


@app.post("/predict", response_model=Response)
async def get_city_coordinates(request: RouteRequest):
    routes = get_routes(request.city_name, request.bus_count, request.interest_points, request.central_points)
 
    return {"success": True, "data": routes}


@app.post("/mock/predict_route", response_model=Response)
async def get_route(request: RouteRequest):
    try:
        route_coordinates = [
            {"lat": 37.7749, "lng": -122.4194},  # Start: San Francisco Downtown
            {"lat": 37.7831, "lng": -122.4181},  # Chinatown
            {"lat": 37.7863, "lng": -122.4015},  # Financial District
            {"lat": 37.7929, "lng": -122.3970},  # Embarcadero
            {"lat": 37.8013, "lng": -122.3905},  # Fisherman's Wharf area
            {"lat": 37.8065, "lng": -122.4127},  # Fort Mason
            {"lat": 37.8026, "lng": -122.4382},  # Marina District
            {"lat": 37.8033, "lng": -122.4618},  # Presidio
            {"lat": 37.8083, "lng": -122.4747},  # Baker Beach area
            {"lat": 37.7925, "lng": -122.4831},  # Richmond District
            {"lat": 37.7694, "lng": -122.4862},  # Sunset District
            {"lat": 37.7621, "lng": -122.4748},  # Inner Sunset
            {"lat": 37.7670, "lng": -122.4577},  # Haight-Ashbury
            {"lat": 37.7682, "lng": -122.4325},  # Hayes Valley
            # {"lat": 37.7749, "lng": -122.4194},  # End: Back to Downtown (circular route)
        ]

        mock2 = {
            "city": {"lat": 32.0568, "lng": 34.7594},
            "lanes": {
                "lane_1": {
                    "stops": [
                        {"lat": 32.0568, "lng": 34.7594},  # Neve Tzedek Center
                        {"lat": 32.0555, "lng": 34.7568},  # Shabazi St/ Pines St
                        {"lat": 32.0572, "lng": 34.7620}   # Eilat St/ Elifelet St
                    ],
                    "route": [
                        {"lat": 32.0568, "lng": 34.7594},  # Starting at Neve Tzedek Center
                        {"lat": 32.0555, "lng": 34.7568},
                        {"lat": 32.0540, "lng": 34.7550},  # Intersection of Shabazi St and Chelouche St
                        {"lat": 32.0530, "lng": 34.7535},  # Intersection of Chelouche St and Eilat St
                        {"lat": 32.0545, "lng": 34.7580},  # Intersection of Eilat St and Elifelet St
                        {"lat": 32.0572, "lng": 34.7620}   # Ending at Eilat St/ Elifelet St
                    ]
                },
                "lane_2": {
                    "stops": [
                        {"lat": 32.0568, "lng": 34.7594},  # Neve Tzedek Center
                        {"lat": 32.0550, "lng": 34.7570},  # Shabazi St/ Rokach St
                        {"lat": 32.0580, "lng": 34.7605}   # Eilat St/ HaMered St
                    ],
                    "route": [
                        {"lat": 32.0568, "lng": 34.7594},  # Starting at Neve Tzedek Center
                        {"lat": 32.0550, "lng": 34.7570},
                        {"lat": 32.0535, "lng": 34.7555},  # Intersection of Shabazi St and Rokach St
                        {"lat": 32.0525, "lng": 34.7540},  # Intersection of Rokach St and Eilat St
                        {"lat": 32.0540, "lng": 34.7585},  # Intersection of Eilat St and HaMered St
                        {"lat": 32.0580, "lng": 34.7605}   # Ending at Eilat St/ HaMered St
                    ]
                }
            }
        }

        # return {"success": True, "route": route_coordinates}
        return {"success": True, "data": mock2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CityCoordinates(BaseModel):
    city: str
    latitude: float
    longitude: float
    country: Optional[str] = None


@app.get("/coordinates/{city}", response_model=CityCoordinates)
async def get_city_coordinates(city: str):
    try:
        # Get the centroid of the city
        gdf = ox.geocode_to_gdf(city)

        if gdf.empty:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")

        # Extract the centroid coordinates and create response
        centroid = gdf.centroid[0]

        # Extract place information
        place_info = gdf.iloc[0]
        country = None
        if 'country' in place_info:
            country = place_info['country']

        return CityCoordinates(
            city=city,
            latitude=centroid.y,
            longitude=centroid.x,
            country=country
        )

    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Error retrieving coordinates: {str(e)}")