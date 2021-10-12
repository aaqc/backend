from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Optional
from pydantic import BaseModel, validator
from typing import Any, Optional

from pydantic.networks import validate_email


class AAQCBaseModel(BaseModel):
    id: int


class AAQCBaseModelOrm(AAQCBaseModel):
    class Config:
        orm_mode = True


class BaseUser(AAQCBaseModel):
    username: str
    email: str
    full_name: str


class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class User(BaseUser):
    email: str
    full_name: str
    groups: list[Group]  # Group


class UserLogin(BaseModel):
    username: str
    email: str
    password: str


class UserCreate(UserLogin):
    full_name: str


class Group(AAQCBaseModel):
    name: str
    members: list[User]


class Drone(AAQCBaseModel):
    owner: Optional[User]
    name: str
    history: list[FlightPath]  # Flightpath


class FlightPath(AAQCBaseModel):
    drone: Drone
    pilot: User
    start: Waypoint
    end: Waypoint
    duration: int
    travel_distance: float


class Waypoint(AAQCBaseModel):
    path: FlightPath
    index: int
    timestamp: int
    longitude: float
    latitude: float
    altitude: float
    heading: float
    speed: float
    battery_level: float


models: list[Any] = [User, UserCreate, Group, Drone, FlightPath, Waypoint]

for model in models:
    model.update_forward_refs()
