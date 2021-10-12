from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Optional
from pydantic import BaseModel
from typing import Any, Optional

from pydantic.networks import EmailStr


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
    email: EmailStr
    password: str
    full_name: str


class User(BaseUser):
    email: EmailStr
    full_name: str
    groups: list[Group]


class UserLogin(BaseModel):
    password: str


class UserLoginEmail(UserLogin):
    email: EmailStr


class UserLoginUsername(UserLogin):
    username: str


class UserLoginFull(UserLoginEmail, UserLoginUsername):
    pass


class UserCreate(UserLoginFull):
    full_name: str


class Group(AAQCBaseModel):
    name: str
    members: list[User]


class Drone(AAQCBaseModel):
    owner: Optional[User] = None
    name: str
    history: list[FlightPath]


class Waypoint(AAQCBaseModel):
    index: int
    timestamp: int
    longitude: float
    latitude: float
    altitude: float
    heading: float
    speed: float
    battery_level: float


class FlightPath(AAQCBaseModel):
    drone: Drone
    pilot: User
    start: Waypoint
    end: Waypoint
    duration: int
    travel_distance: float
    waypoints: list[Waypoint]


models: list[Any] = [User, UserCreate, Group, Drone, FlightPath, Waypoint]

for model in models:
    model.update_forward_refs()
