from pydantic import BaseModel
from typing import Tuple, List, Dict, Optional

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


class InterestPoint(BaseModel):
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
    grade: int

    class Config:
        frozen = True  # Makes it hashable
    #     fields = {'class_': 'class'}


class RouteRequest(BaseModel):
    city_name: Optional[str] = None
    bus_count: Optional[int] = None
    interest_points: Optional[List[InterestPoint]] = None
    central_points: Optional[List[OsmLocation]] = None


class Coordinate(BaseModel):
    lat: float
    lng: float


class RouteResponse(BaseModel):
    success: bool
    route: List[Coordinate]


class Lane(BaseModel):
    stops: List[Coordinate]
    route: List[Coordinate]


class Data(BaseModel):
    city: Coordinate
    lanes: Dict[str, Lane]


class Response(BaseModel):
    success: bool
    data: Data