# from fastapi import FastAPI
# from pydantic import BaseModel
# import random  # Replace this with your DeepRL model
#
# app = FastAPI()
#
# # Input Schema
# class RequestData(BaseModel):
#     city_name: str
#     num_buses: int
#
# # Fake route generation (Replace with your RL model)
# def generate_routes(city_name: str, num_buses: int):
#     return {"city": city_name, "routes": [f"Route {i+1}" for i in range(num_buses)]}
#
# @app.post("/generate_routes")
# def generate_bus_routes(data: RequestData):
#     routes = generate_routes(data.city_name, data.num_buses)
#     return {"success": True, "data": routes}
#
# # Run with: uvicorn main:app --reload

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import osmnx as ox
from osm_env import OSMEnv
from agent import MAPPOAgent
import logic as logic
import random

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteRequest(BaseModel):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    city_name: Optional[str] = None


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
    lane_3: Lane
    lane_1: Lane
    lane_2: Lane


class Response(BaseModel):
    success: bool
    data: Data


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


class PredictRequest(BaseModel):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    city_name: Optional[str] = None


@app.post("/predict", response_model=Response)
async def get_city_coordinates(request: PredictRequest):
    def test(agent_class, env_class, num_agents, state_size, max_action_size, model_paths, episodes=1, show_plot=True, save_path=None):
        env = env_class()
        agent = agent_class(state_size, max_action_size, num_agents, env.node_to_index)

        # Load trained models
        for i in range(num_agents):
            agent.actor[i].load_weights(model_paths[i])
            print(f"Loaded model for agent {i} from {model_paths[i]}")

        for episode in range(episodes):
            obs, _ = env.reset()
            done = {agent_name: False for agent_name in env.agents}
            step_count = 0

            while not all(done.values()):
                actions = {}
                for i, agent_name in enumerate(env.agents):
                    valid_actions = env.get_valid_actions(i)
                    if len(valid_actions) > 0 and not done[agent_name]:
                        action = agent.get_action(obs[agent_name], i, valid_actions)
                        actions[agent_name] = action
                    else:
                        done[agent_name] = True
                        actions[agent_name] = -1

                next_obs, rewards, done, _ = env.step(actions, done)

                for agent_name in env.agents:
                    if not done[agent_name]:
                        obs[agent_name] = next_obs[agent_name]

                step_count += 1
                if step_count > 100 * 3: # max_steps_per_episode
                    print("Breaking test loop, agent possibly stuck")
                    break

            final_trail = {}
            for agent_name in env.agents:
                final_trail[agent_name] = [
                    (env.G.nodes[pos]['y'], env.G.nodes[pos]['x'])  # Assuming 'y' is lat and 'x' is lng
                    for pos in env.trails[agent_name]
                ]

            return final_trail   

    model_paths = [f"./models/actor_{i}.h5" for i in range(3)]

    final_trail = test(
        agent_class=MAPPOAgent,
        env_class=OSMEnv,
        num_agents=3,
        state_size=2,
        max_action_size=8,
        model_paths=model_paths,
        episodes=1,
        show_plot=True,
        save_path="test_route"  # will save as test_route_ep1.png
    )

    def transform_trails_to_lanes(final_trail):
        final_lanes = {}

        for i, (agent_name, route) in enumerate(final_trail.items(), start=1):
            # Convert route points to the required format
            formatted_route = [{"lat": lat, "lng": lng} for lat, lng in route]
            
            # Randomly select a few stops from the route
            num_stops = min(3, len(formatted_route))  # Choose up to 3 stops or less if the route is small
            stops = random.sample(formatted_route, num_stops)

            # Construct the final structure
            final_lanes[f"lane_{i}"] = {
                "stops": stops,
                "route": formatted_route
            }

        return final_lanes

    # Example usage:
    final_lanes = transform_trails_to_lanes(final_trail)

    print(final_lanes)

    final_lanes['city'] = final_lanes['lane_1']['route'][0]
 
    return {"success": True, "data": final_lanes}
