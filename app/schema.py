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
    email: EmailStr
    full_name: str


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str


class User(BaseUser, AAQCBaseModelOrm):
    email: EmailStr
    full_name: str
    groups: list[BaseGroup] = []


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


class BaseGroup(AAQCBaseModel):
    name: str


class Group(BaseGroup):
    members: list[User] = []


class Drone(AAQCBaseModel):
    owner: Optional[User] = None
    name: str
    history: list[FlightPath]


class Waypoint(AAQCBaseModel):
    timestamp: int
    longitude: float
    latitude: float
    altitude: float
    heading: float

    """speed of the drone when entering the waypoint in m/s"""
    speed: float
    """battery level of the drone when entering the waypoint in %"""
    battery_level: float


class FlightPath(AAQCBaseModel):
    drone: Drone
    pilot: User
    start: Waypoint
    end: Waypoint
    duration: int
    travel_distance: float
    waypoints: list[Waypoint]


class AuthResponse(BaseModel):
    token: str


models: list[Any] = [User, UserCreate, Group, Drone, FlightPath, Waypoint, BaseGroup]

for model in models:
    model.update_forward_refs()
